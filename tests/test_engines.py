import unittest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
else:
    sys.path.remove(str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR))

# Strip external editable finders from sys.meta_path
for finder in list(sys.meta_path):
    finder_repr = repr(finder).lower()
    if "lightsense" in finder_repr or "nifty" in finder_repr:
        sys.meta_path.remove(finder)

from app.data_engines.apollo_streamer import ApolloStreamEngine
from app.data_engines.customs_engine import CustomsTradeEngine
from app.data_engines.startup_icp_engine import StartupICPEngine
from app.services.verifier import WaterfallEmailVerifier
from app.services.ai_generator import AIEmailGenerator
from app.services.deliverability import DeliverabilityService
from app.services.crm import CRMService
from app.services.templates_vault import HumanizedTemplatesVault
from app.data_engines.social_parser import SocialParserEngine
from app.services.harvey_agent import HarveyAutonomousSDRAgent

class TestEximFlowEngines(unittest.TestCase):

    def setUp(self):
        self.apollo = ApolloStreamEngine()
        self.customs = CustomsTradeEngine()
        self.startups = StartupICPEngine()
        self.crm = CRMService()
        self.social = SocialParserEngine()
        self.harvey = HarveyAutonomousSDRAgent()

    def test_apollo_stats_and_stream(self):
        stats = self.apollo.get_stats()
        self.assertTrue(stats.get("available"))
        self.assertIn("18.", str(stats.get("size_compressed_gb")))
        # Search leads in Apollo stream
        leads = self.apollo.search_leads(query="procurement", limit=3)
        self.assertGreater(len(leads), 0)
        self.assertTrue(all("@" in l["email"] for l in leads))

    def test_customs_search(self):
        results = self.customs.search_customs(product="Basmati", limit=5)
        self.assertGreater(len(results), 0)
        lead = results[0]
        self.assertIn("Basmati", lead["product_interest"])
        self.assertIn("TEU", lead["annual_teu_volume"])

    def test_startup_icp_search_and_synonyms(self):
        # Test acronym match for CTO
        cto_leads = self.startups.search_startups(query="CTO")
        self.assertGreater(len(cto_leads), 0)
        # Test country filter
        uk_leads = self.startups.search_startups(country="United Kingdom")
        self.assertGreater(len(uk_leads), 0)
        self.assertEqual(uk_leads[0]["country"], "United Kingdom")

    def test_email_verifier(self):
        # Valid corporate email
        v1 = WaterfallEmailVerifier.verify("buyer@corporatetrade.com")
        self.assertEqual(v1["status"], "SAFE_TO_SEND")
        self.assertGreaterEqual(v1["score"], 85)

        # Invalid format
        v2 = WaterfallEmailVerifier.verify("not-an-email")
        self.assertEqual(v2["status"], "DO_NOT_SEND")

        # Disposable domain
        v3 = WaterfallEmailVerifier.verify("test@mailinator.com")
        self.assertEqual(v3["status"], "DO_NOT_SEND")
        self.assertTrue(v3["is_disposable"])

        # Role-based prefix
        v4 = WaterfallEmailVerifier.verify("info@corporatetrade.com")
        self.assertEqual(v4["status"], "ACCEPTABLE_RISKY")
        self.assertTrue(v4["is_role_account"])

    def test_ai_sequence_generator(self):
        seq = AIEmailGenerator.generate_sequence(
            prospect_name="Arthur Pendelton",
            prospect_title="Chief Procurement Officer",
            prospect_company="Titan Piping",
            product_category="Stainless Steel Flanges"
        )
        self.assertEqual(len(seq["sequences"]), 3)
        self.assertIn("touch1", seq)
        self.assertIn("touch2", seq)
        self.assertIn("touch3", seq)
        self.assertTrue(seq["spam_analysis"]["score"] >= 70)

    def test_deliverability_and_warmup(self):
        dns = DeliverabilityService.generate_dns_records("global-exports.com")
        types = [r["type"] for r in dns["records"]]
        self.assertIn("TXT", types)
        self.assertIn("CNAME", types)
        self.assertIn("MX", types)

        warmup = DeliverabilityService.calculate_warmup_schedule(120)
        self.assertEqual(len(warmup), 21)
        self.assertEqual(warmup[0]["cold_emails"], 0)
        self.assertGreater(warmup[-1]["cold_emails"], 0)

        cap = DeliverabilityService.calculate_inbox_capacity(5000)
        self.assertGreaterEqual(cap["required_mailboxes"], 4)
        self.assertGreaterEqual(cap["required_secondary_domains"], 2)

    def test_crm_pipeline_and_triage(self):
        initial_count = len(self.crm.get_all_leads())
        new_lead = self.crm.add_lead({
            "name": "David Miller",
            "email": "d.miller@transatlantic.com",
            "title": "Director of Imports",
            "company": "Transatlantic Foods"
        })
        self.assertEqual(len(self.crm.get_all_leads()), initial_count + 1)

        # Update stage
        updated = self.crm.update_lead_stage(new_lead["id"], "call_booked")
        self.assertTrue(updated)

        # Triage test
        triage_positive = self.crm.classify_email_reply("Let's set up a call for Tuesday 2pm")
        self.assertEqual(triage_positive["sentiment"], "positive")
        self.assertIn("DISCOVERY CALL", triage_positive["classification"])

        triage_unsub = self.crm.classify_email_reply("Please unsubscribe our address")
        self.assertEqual(triage_unsub["sentiment"], "negative")
        self.assertIn("UNSUBSCRIBE", triage_unsub["classification"])

        # CSV Export
        csv_data = self.crm.export_csv_smartlead()
        self.assertIn("First Name,Last Name,Email", csv_data)
        self.assertIn("David,Miller,d.miller@transatlantic.com", csv_data)

    def test_batch_verify_and_delete(self):
        batch_res = self.crm.batch_verify_leads(WaterfallEmailVerifier)
        self.assertGreaterEqual(batch_res["total_verified"], 4)
        self.assertGreaterEqual(batch_res["safe_to_send"], 1)

        # Delete lead test
        leads = self.crm.get_all_leads()
        first_id = leads[0]["id"]
        success = self.crm.delete_lead(first_id)
        self.assertTrue(success)

    def test_humanized_templates_vault(self):
        templates = HumanizedTemplatesVault.get_all_templates()
        self.assertGreaterEqual(len(templates), 5)
        # Check that none of the templates contain robotic AI clichés
        for tmpl in templates:
            combined = f"{tmpl['touch1_subject']} {tmpl['touch1_body']}".lower()
            self.assertNotIn("cutting-edge", combined)
            self.assertNotIn("revolutionary", combined)
            self.assertNotIn("game-changing", combined)
            self.assertNotIn("i hope this email finds you well", combined)

    def test_client_proposal_generator(self):
        prop_growth = HumanizedTemplatesVault.generate_client_proposal(
            exporter_name="Aarav Sharma",
            exporter_company="Surat Agro Exports",
            product="Organic Turmeric",
            tier="growth"
        )
        self.assertIn("65,000", prop_growth["fee"])
        self.assertIn("Organic Turmeric", prop_growth["proposal_text"])

        prop_hybrid = HumanizedTemplatesVault.generate_client_proposal(
            exporter_name="Amit Shah",
            exporter_company="Morbi Ceramics Ltd",
            product="Vitrified Tiles",
            tier="hybrid"
        )
        self.assertIn("25,000", prop_hybrid["fee"])

    def test_pdf_proposal_generator(self):
        from app.services.pdf_generator import PDFProposalGenerator
        filename, pdf_bytes = PDFProposalGenerator.create_proposal_pdf(
            exporter_name="Aarav Sharma",
            exporter_company="Surat Agro Exports Ltd",
            product="Organic Turmeric & Spices",
            target_country="United States & Germany",
            tier="growth"
        )
        self.assertTrue(filename.endswith(".pdf"))
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_social_parser_engine(self):
        # Search by hashtag/keyword
        leads = self.social.search_social_leads(query="spices", limit=5)
        self.assertGreater(len(leads), 0)
        self.assertTrue(all("@" in l["email"] for l in leads))
        self.assertIn("Instagram", leads[0]["data_source"])

        # Reel / target parse simulation
        reel_leads = self.social.parse_reel_or_profile_target(
            target_input="https://www.instagram.com/reel/DfFf3r2tHEn/",
            niche="Spices & Agro"
        )
        self.assertGreater(len(reel_leads), 0)

    def test_social_parser_csv_import(self):
        sample_csv = """Username,Full Name,Email,Phone,Bio,Website,Category,Country
dutchherbs,Dutch Herbs BV,info@dutchherbs.nl,+31 20 555 1234,Importer of organic bulk tea and herbs,https://dutchherbs.nl,Agro Import,Netherlands
austinfoodsupply,Austin Food Supply LLC,procure@austinfood.com,+1 512-555-8901,Wholesale restaurant supply Texas,https://austinfood.com,Wholesale,United States"""
        result = self.social.import_parser_im_csv(sample_csv)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["imported_count"], 2)
        self.assertEqual(result["leads"][0]["email"], "info@dutchherbs.nl")

    def test_harvey_autonomous_agent(self):
        # 1. Configuration
        status = self.harvey.configure_profile(
            business_name="Surat Spices Ltd",
            business_offering="Direct processor of organic turmeric & black pepper",
            icp_description="Food importing directors in North America",
            target_geography="United States, Canada",
            mode="review_first"
        )
        self.assertEqual(status["business_name"], "Surat Spices Ltd")
        self.assertEqual(status["mode"], "review_first")

        # 2. Autonomous cycle execution
        cycle_res = self.harvey.run_autonomous_cycle(
            customs_engine=self.customs,
            apollo_engine=self.apollo,
            social_engine=self.social,
            verifier_engine=WaterfallEmailVerifier,
            crm_engine=self.crm
        )
        self.assertEqual(cycle_res["cycle_status"], "completed")
        self.assertGreater(cycle_res["candidates_scouted"], 0)
        self.assertGreater(cycle_res["emails_staged"], 0)

        # 3. Outbox approval
        rep = self.harvey.get_status_report()
        staged_items = [o for o in rep["outbox"] if o["status"] == "STAGED_REVIEW"]
        if staged_items:
            first_staged = staged_items[0]
            approved = self.harvey.approve_outbox_email(first_staged["id"])
            self.assertTrue(approved)

        # 4. Metrics and Logs
        final_rep = self.harvey.get_status_report()
        self.assertGreater(len(final_rep["logs"]), 0)
        self.assertGreater(final_rep["metrics"]["staged_outbox"], 0)

if __name__ == "__main__":
    unittest.main()

