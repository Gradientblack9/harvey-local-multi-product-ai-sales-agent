"""Invented, explicitly labelled input records. No generated AI outputs are seeded."""
from .db import connect, now

COMPANIES = [
 ("Meridian Labs","Avery Chen","VP of Engineering","B2B SaaS",180,"Austin, US","Developer platform. Hiring 14 engineers after a $12M Series A. Customer access reviews are tracked in spreadsheets. A security lead's sample note mentions upcoming SOC 2 audit and delayed enterprise deals."),
 ("Northstar Commerce","Jordan Blake","Head of Operations","E-commerce",95,"London, UK","Online retailer expanding into two EU markets. Support queue doubled this quarter. Uses separate spreadsheets for supplier onboarding; hiring an operations analyst and evaluating helpdesk automation."),
 ("Forma Health","Samira Patel","Chief Operating Officer","Healthcare",260,"Bengaluru, IN","Clinic software provider serving 40 clinics. Announced two new hospital pilots in this fictional dataset. Manual patient-support routing and vendor access approvals delay onboarding. Security compliance review planned this year."),
 ("Arcwell Finance","Leo Martin","Director of Security","Financial services",420,"New York, US","Payments startup with a sample announcement of a $25M funding round. Hiring cloud security engineers. Enterprise customers require evidence of access controls. Existing support desk handles tickets manually."),
 ("Juniper Studio","Elena Rossi","Founder","Design services",18,"Berlin, DE","Small design consultancy. Stable headcount, no recent fundraising or hiring mentioned. Relies on email for client support. Has no compliance initiative, and a limited software budget."),
 ("Orbit Logistics","Noah Williams","VP of Customer Experience","Logistics",330,"Singapore, SG","Regional shipping software business. Opening a new customer service centre; hiring 20 support agents. Sample notes report repetitive shipment-status tickets and slow escalations. Uses a cloud warehouse for event data."),
 ("Cedar Analytics","Maya Singh","CTO","B2B SaaS",75,"Pune, IN","Analytics platform switching from shared admin accounts to role-based access. Preparing its first SOC 2 audit. Hiring a platform engineer. Support enquiries are low volume and handled by founders."),
 ("Solstice Energy","Oliver Reed","Head of IT","Energy",650,"Denver, US","Renewable project operator integrating three newly acquired sites. Legacy vendor accounts need review. Customer enquiries are mostly phone based. Sample procurement note says security consolidation begins next quarter."),
 ("Brightpath Learning","Zoe Park","Head of Customer Success","EdTech",140,"Toronto, CA","Online learning platform. Support volume rises during student intake; 60% of sample tickets concern enrolment and passwords. Hiring customer success managers and considering an automated knowledge base."),
 ("Tidal Manufacturing","Arjun Mehta","IT Director","Manufacturing",850,"Ahmedabad, IN","Manufacturer with on-premise ERP. Paused software procurement for six months in the sample record. Small service desk; no funding, expansion or hiring signals documented. Vendor access reviews are annual."),
 ("Kiteworks Cloud","Isabella Davis","VP of Engineering","B2B SaaS",210,"Seattle, US","Cloud integration vendor pursuing regulated enterprise accounts. Security questionnaires take two weeks; audit evidence lives in shared drives. Hiring a compliance manager. Support team has 12 agents across time zones."),
 ("Willow Market","Ethan Brooks","Customer Support Lead","E-commerce",55,"Melbourne, AU","Subscription retailer with 8,000 fictional monthly orders. Customer support runs from a shared inbox. Hiring two agents; returns and delivery questions dominate the sample queue. Budget review scheduled next month."),
]
THREADS = [
 "Sales: Would a short overview of our product be useful?\nProspect: Yes, please send the details. We are evaluating options this month and can meet next Tuesday.",
 "Sales: Could this help your team?\nProspect: Thanks, but we already renewed our existing platform and do not need another solution.",
 "Sales: Is this a priority for your team?\nProspect: It may be relevant after our budget review in January. Please follow up then.",
 "Sales: May I share an overview?\nProspect: Remove me from your list. Do not contact me again.",
 "Sales: Would you like a walkthrough?\nProspect: Automatic reply: I am away from the office until Monday. For urgent requests use our service desk.",
]

def seed():
    with connect() as db:
        if db.execute("SELECT count(*) FROM products").fetchone()[0]:
            return
        products = [
            ("Sentinel","Harbor Systems","Harbor Systems is a fictional software company building practical tools for growing businesses. Its products address security operations and customer support.","An access governance and audit readiness workspace that automates access reviews, organises SOC 2 evidence and tracks vendor permissions.","B2B software and regulated businesses with 50-500 employees preparing enterprise security audits.","Reduce manual audit preparation and make access reviews repeatable.","green"),
            ("Relay","Harbor Systems","Harbor Systems is a fictional software company building practical tools for growing businesses. Its products address security operations and customer support.","A customer support workspace that routes tickets, suggests knowledge base answers and summarises conversations for service teams.","E-commerce, logistics and online services with 20-500 employees and growing support queues.","Reduce repetitive support work and improve response times without expanding the team at the same rate.","blue"),
        ]
        for p in products:
            pid = db.execute("INSERT INTO products(name,company_name,company_info,description,target_market,value_proposition,color,sample,created_at) VALUES (?,?,?,?,?,?,?,1,?)", (*p, now())).lastrowid
            prospect_ids = []
            for company in COMPANIES:
                prospect_ids.append(db.execute("INSERT INTO prospects(product_id,company,contact_name,title,industry,employees,location,notes,sample,created_at) VALUES (?,?,?,?,?,?,?,?,1,?)", (pid,*company,now())).lastrowid)
            for prospect_id, thread in zip(prospect_ids,THREADS):
                db.execute("INSERT INTO replies(product_id,prospect_id,thread,sample,created_at) VALUES (?,?,?,1,?)", (pid,prospect_id,thread,now()))
