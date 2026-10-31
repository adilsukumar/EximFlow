import os
import io
from datetime import datetime
from typing import Dict, Any, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically calculate total page count
    and render formal corporate running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#64748b'))

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(40, 34, 555, 34)
        self.drawString(40, 24, 'CONFIDENTIAL & PROPRIETARY  |  EXIMFLOW TRADE ADVISORY SERVICES')
        self.drawRightString(555, 24, f'Page {self._pageNumber} of {page_count}')

        # Running Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(40, 810, 'EXIMFLOW TRADE ADVISORY  |  COMMERCIAL ENGAGEMENT AGREEMENT')
            self.drawRightString(555, 810, 'STATEMENT OF WORK')
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)

        self.restoreState()


class PDFProposalGenerator:
    """
    Generates formal, natural, print-ready corporate engagement agreements (PDF)
    for B2B commodity exporters and international trade clients.
    """

    @classmethod
    def create_proposal_pdf(
        cls,
        exporter_name: str = "Aarav Sharma",
        exporter_company: str = "Surat Agro Exports Ltd",
        product: str = "Organic Turmeric & Spices",
        target_country: str = "United States & Germany",
        tier: str = "growth"
    ) -> Tuple[str, bytes]:
        tier_clean = (tier or "growth").lower()
        if tier_clean == "starter":
            tier_display = "STARTER ADVISORY TIER"
            fee_display = "INR 35,000 / month"
            leads_target = "500 Verified Importers"
            meeting_target = "2-3 Qualified Buyer Discovery Calls"
            infra_desc = "Technical provisioning and warmup monitoring of 2 dedicated outreach mailboxes across 1 secondary domain."
        elif tier_clean == "hybrid":
            tier_display = "PERFORMANCE HYBRID TIER"
            fee_display = "INR 25,000 / month + Performance Fee"
            leads_target = "1,000 Verified Importers"
            meeting_target = "Pay-per-meeting alignment (INR 5,000 / verified discovery call)"
            infra_desc = "Technical provisioning and warmup monitoring of 4 dedicated outreach mailboxes across 2 secondary domains."
        else:  # growth default
            tier_display = "GROWTH ENGAGEMENT TIER"
            fee_display = "INR 65,000 / month"
            leads_target = "1,500 Verified Importers"
            meeting_target = "4-6 Qualified International Discovery Calls"
            infra_desc = "Technical provisioning and warmup monitoring of 4 dedicated outreach mailboxes across 2 secondary domains."

        today_str = datetime.now().strftime("%B %d, %Y")
        comp_hash = abs(hash(exporter_company)) % 9000 + 1000
        ref_id = f"EXIM-AGR-{datetime.now().strftime('%Y')}-{comp_hash}"

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=42,
            bottomMargin=44
        )

        styles = getSampleStyleSheet()

        h_title = ParagraphStyle('HTitle', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=colors.HexColor('#0f2942'))
        h_sub = ParagraphStyle('HSub', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#64748b'))
        doc_title = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=colors.HexColor('#0f172a'), alignment=1)
        sec_head = ParagraphStyle('SecHead', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#0f2942'), spaceBefore=8, spaceAfter=3)
        body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#334155'))
        body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=colors.HexColor('#0f172a'))
        meta_lbl = ParagraphStyle('MetaLbl', fontName='Helvetica-Bold', fontSize=7, leading=9, textColor=colors.HexColor('#64748b'))
        meta_val = ParagraphStyle('MetaVal', fontName='Helvetica-Bold', fontSize=8, leading=10.5, textColor=colors.HexColor('#0f172a'))

        story = []

        # =========================================================================
        # PAGE 1: LETTERHEAD, TITLE, METADATA, PURPOSE, SOW, COMMERCIAL TERMS
        # =========================================================================

        # 1. Corporate Letterhead
        h_table = Table([
            [Paragraph('EXIMFLOW TRADE ADVISORY SERVICES', h_title), Paragraph(f'<b>REF:</b> {ref_id}<br/><b>DATE:</b> {today_str}', h_sub)],
            [Paragraph('Global Trade Business Development & Direct Sourcing Representation', h_sub), Paragraph('<b>STATUS:</b> Binding Commercial Retainer', h_sub)]
        ], colWidths=[335, 180])
        h_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
        ]))
        story.append(h_table)
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#0f2942'), spaceBefore=2, spaceAfter=8))

        # 2. Document Title Banner
        b_table = Table([[
            Paragraph(
                'COMMERCIAL ENGAGEMENT AGREEMENT & STATEMENT OF WORK<br/>'
                '<font size="7.5" color="#475569">International Wholesale Buyer Origination & Pipeline Development Retainer</font>',
                doc_title
            )
        ]], colWidths=[515])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('LINEBEFORE', (0,0), (0,-1), 3.5, colors.HexColor('#0f2942')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(b_table)
        story.append(Spacer(1, 6))

        # 3. Engagement Metadata Table
        m_table = Table([
            [Paragraph('CLIENT EXPORTER / MANUFACTURER', meta_lbl), Paragraph('COMMERCIAL RETAINER PACKAGE', meta_lbl)],
            [
                Paragraph(f'{exporter_company}<br/><font size="7" color="#64748b">Attn: {exporter_name}, Authorized Signatory</font>', meta_val),
                Paragraph(f'{tier_display} ({fee_display})<br/><font size="7" color="#059669">Target: {meeting_target}</font>', meta_val)
            ],
            [Paragraph('TARGET COMMODITY / PRODUCT LINE', meta_lbl), Paragraph('TARGET SOURCING GEOGRAPHIES', meta_lbl)],
            [
                Paragraph(f'{product}', meta_val),
                Paragraph(f'{target_country} (Customs Manifest Registry)', meta_val)
            ],
        ], colWidths=[257, 258])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(m_table)
        story.append(Spacer(1, 6))

        # 4. Section 1: Purpose & Recitals
        story.append(Paragraph('1. Purpose & Scope of Commercial Engagement', sec_head))
        story.append(Paragraph(
            f'This Commercial Engagement Agreement is executed between EximFlow Trade Advisory ("Advisory Firm") '
            f'and {exporter_company} ("Client"). The Client engages EximFlow to execute systematic international market research, '
            f'verified foreign wholesale buyer origination, and direct commercial correspondence for {product} across target overseas territories. '
            f'Both parties commit to professional conduct and commercial confidentiality throughout the operating term.',
            body
        ))
        story.append(Spacer(1, 4))

        # 5. Section 2: Statement of Work & Operational Deliverables
        story.append(Paragraph('2. Scope of Work & Operational Deliverables', sec_head))
        sow_data = [
            [Paragraph('<b>Deliverable Stream</b>', body_bold), Paragraph('<b>Operational Scope & Implementation Standards</b>', body_bold)],
            [
                Paragraph('<b>2.1 Trade Intelligence & Importer Sourcing</b>', body),
                Paragraph(f'Systematic extraction and verification of foreign customs shipping manifests (Bills of Lading) and verified B2B trade intelligence. Identifying {leads_target} active container importers, bulk processors, and wholesale distributors in target jurisdictions.', body)
            ],
            [
                Paragraph('<b>2.2 Communications Infrastructure</b>', body),
                Paragraph(f'{infra_desc} Full protocol authentication including SPF, DKIM (2048-bit RSA), and strict DMARC enforcement to guarantee primary commercial inbox delivery.', body)
            ],
            [
                Paragraph('<b>2.3 Direct Trade Correspondence</b>', body),
                Paragraph('Execution of fact-based, customized trade correspondence highlighting direct manufacturer pricing, harvest origin, moisture/mesh specifications, Incoterms (FOB/CIF), lab compliance (SGS, FDA, BRC), and sample dispatch offers. Zero generic marketing language.', body)
            ],
            [
                Paragraph('<b>2.4 Buyer Triage & Video Meetings</b>', body),
                Paragraph(f'Active screening and triaging of incoming commercial inquiries, resolving technical specification questions, and coordinating {meeting_target} directly on {exporter_company} commercial leadership calendar.', body)
            ]
        ]
        sow_table = Table(sow_data, colWidths=[140, 375])
        sow_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(sow_table)
        story.append(Spacer(1, 6))

        # 6. Section 3: Commercial Retainer & Payment Terms
        story.append(Paragraph('3. Commercial Retainer & Payment Terms', sec_head))
        story.append(Paragraph(
            f'<b>3.1 Monthly Operating Retainer:</b> The Client agrees to a fixed monthly retainer of {fee_display} '
            f'per 30-day operating sprint, payable in advance upon electronic invoice transmission via wire transfer / NEFT.',
            body
        ))
        story.append(Paragraph(
            f'<b>3.2 Performance SLA Commitment:</b> EximFlow commits to the verified outreach volume of {leads_target} '
            f'and the targeted coordination of {meeting_target} per 30-day operating sprint.',
            body
        ))
        story.append(Paragraph(
            '<b>3.3 Out-of-Pocket Expenses:</b> Secondary sending domain registrations, server mailbox hosting, and verified manifest '
            'data feeds are fully inclusive within the retainer fee. No supplemental software charges apply.',
            body
        ))

        # =========================================================================
        # PAGE BREAK TO PAGE 2
        # =========================================================================
        story.append(PageBreak())

        # =========================================================================
        # PAGE 2: UNDERTAKINGS, EXCLUSIVITY, TERMINATION, GOVERNING LAW, SIGNATURES
        # =========================================================================
        story.append(Spacer(1, 14))

        # 7. Section 4: Client Obligations & Technical Undertakings
        story.append(Paragraph('4. Client Undertakings & Operational Collaboration', sec_head))
        story.append(Paragraph(
            'To ensure maximum commercial conversion and rapid qualification of international buyers, the Client agrees to the following operational commitments:',
            body
        ))
        story.append(Spacer(1, 4))
        u_data = [
            [Paragraph('<b>Item</b>', body_bold), Paragraph('<b>Client Commitment Description</b>', body_bold)],
            [
                Paragraph('<b>4.1 Technical Specifications</b>', body),
                Paragraph('Provide accurate product specification sheets, Certificates of Analysis (COA), export packaging parameters, and regulatory certifications (FSSAI, APEDA, BRC, FDA registration) prior to campaign initiation.', body)
            ],
            [
                Paragraph('<b>4.2 Commercial Floor Matrix</b>', body),
                Paragraph('Establish competitive FOB (Nhava Sheva/Mundra) and CIF target destination price guidelines, standard payment terms (e.g. 20% advance / 80% against BL or LC at sight), and Minimum Order Quantities (MOQ).', body)
            ],
            [
                Paragraph('<b>4.3 Sample Dispatch Protocol</b>', body),
                Paragraph('Maintain ready stock of 500g commercial evaluation samples and dispatch via international express air courier (DHL/FedEx) to qualified buyers within 48 hours of confirmed buyer request.', body)
            ],
            [
                Paragraph('<b>4.4 Meeting Attendance</b>', body),
                Paragraph('Ensure qualified commercial sales or export management personnel attend all pre-scheduled video discovery conferences with verified overseas buyers promptly.', body)
            ]
        ]
        u_table = Table(u_data, colWidths=[140, 375])
        u_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(u_table)
        story.append(Spacer(1, 6))

        # 8. Section 5: Exclusivity, Ownership & Non-Disclosure
        story.append(Paragraph('5. Exclusivity, Ownership & Non-Disclosure', sec_head))
        story.append(Paragraph(
            f'<b>5.1 Proprietary Data Ownership:</b> All foreign buyer contact records, verified manifest intelligence, correspondence histories, '
            f'and commercial RFQs developed during the term of this engagement are and shall permanently remain the exclusive commercial property of {exporter_company}.',
            body
        ))
        story.append(Paragraph(
            '<b>5.2 Mutual Confidentiality:</b> Both parties agree to hold all commercial terms, client pricing structures, trade secrets, and supplier data '
            'in strict confidence, and shall not disclose any proprietary materials to third parties without prior written consent.',
            body
        ))
        story.append(Paragraph(
            f'<b>5.3 Territorial Non-Compete Exclusivity:</b> EximFlow covenants that during the active term of this Agreement, it shall not represent or conduct '
            f'outbound buyer business development for any direct competing exporter of {product} in the designated target jurisdictions.',
            body
        ))
        story.append(Spacer(1, 6))

        # 9. Section 6: Term, Renewal & Termination Protocol
        story.append(Paragraph('6. Term, Renewal & Termination Protocol', sec_head))
        story.append(Paragraph(
            '<b>6.1 Operating Sprint Term:</b> This Agreement commences on the Effective Date and continues for a primary term of 30 days, '
            'renewing automatically for successive 30-day operating periods upon invoice settlement.',
            body
        ))
        story.append(Paragraph(
            '<b>6.2 Mutual Termination:</b> Either party may conclude the engagement without cause by delivering fourteen (14) calendar days written notice '
            'prior to the end of any 30-day operating term. Upon conclusion, all contact data and technical documentation shall be transitioned to the Client.',
            body
        ))
        story.append(Spacer(1, 6))

        # 10. Section 7: Governing Law & Jurisdiction
        story.append(Paragraph('7. Governing Law & Dispute Resolution', sec_head))
        story.append(Paragraph(
            'This Agreement shall be construed and governed in accordance with standard international commercial trade practices. '
            'Any dispute arising out of or in connection with this Agreement shall first be resolved through good-faith executive consultation, '
            'failing which it shall be referred to standard commercial arbitration.',
            body
        ))
        story.append(Spacer(1, 8))

        # 11. Section 8: Acceptance & Execution
        story.append(Paragraph('8. Acceptance, Authorization & Execution', sec_head))
        story.append(Paragraph(
            'By signing below, the authorized executive representatives of the Parties confirm their agreement to the terms, '
            'deliverables, and commercial stipulations set forth in this Statement of Work.',
            body
        ))
        story.append(Spacer(1, 6))

        sig_data = [
            [
                Paragraph('<b>ACCEPTED & CONFIRMED FOR CLIENT:</b>', meta_lbl),
                Paragraph('', meta_lbl),
                Paragraph('<b>ACCEPTED & CONFIRMED FOR EXIMFLOW:</b>', meta_lbl)
            ],
            [
                Paragraph(f'<b>{exporter_company}</b><br/><br/><br/>________________________________________<br/><b>{exporter_name}</b><br/>Authorized Signatory & Director<br/>Date: ________________________<br/><br/>[Company Stamp / Seal]', body),
                Paragraph('', body),
                Paragraph('<b>EximFlow Trade Advisory Services</b><br/><br/><br/>________________________________________<br/><b>Authorized Partner</b><br/>Head of Global Client Partnerships<br/>Date: ________________________<br/><br/>[Corporate Seal]', body)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[245, 25, 245])
        sig_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (0,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('BOX', (2,0), (2,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sig_table)

        doc.build(story, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        clean_filename = f"EximFlow_Agreement_{exporter_company.replace(' ', '_').replace('/', '_')}.pdf"
        return clean_filename, pdf_bytes
