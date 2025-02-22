from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, customer_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_info = customer_info
    
    def header(self):
        # Logo
        self.image('C:\\Users\\serge\\Desktop\\EDIFY\\Logos & Media\\Logo.png', x=230, y=8, w=33)
        
        x_position = 230
        y_position = 43

        # Company Name
        self.set_xy(x_position, y_position)
        self.set_text_color(5, 132, 244)
        self.set_font('Helvetica', 'B', 12) 
        self.cell(0, 10, 'EdifyAnalytics', 0, 2, 'R')

        # Setting text color to black for the company details
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 10)
        details = [
            'Data-driven insights for smarter decisions',
            'Toms River, NJ 08753',
            '(848)238-6276',
            'spersoff@edifyanalytics.com'
        ]
        y_position += 10  # Moving down slightly for company details
        for detail in details:
            self.set_xy(x_position, y_position)
            self.cell(0, 6, detail, 0, 2, 'R')
            y_position += 6  # Increment the y-position based on the height of the cell

        # Reset position for customer details
        self.set_xy(10, y_position - (6 * len(details)))
        self.set_font('Helvetica', '', 12)
        self.cell(0, 10, "Invoice to:", 0, 2, 'L')  
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 10, self.customer_info, 0, 'L')
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'R')
    
    def add_invoice_items(self, items):
        self.set_font('Helvetica', '', 12)
        col_width = [50, 50, 50, 50, 50]  # Adjusted widths for landscape
        self.ln(10)
        # headers
        headers = ["FEE DESCRIPTION", "FEE CODE", "DESCRIPTION", "INVOICE AMOUNT", "LINE TOTAL"]
        
        # Set fill color to 0433BE
        self.set_fill_color(2, 29, 107)  # Converted hexadecimal to RGB
        # Set text color to off white
        self.set_text_color(240, 240, 240)  # Adjust values as per your need for "just off white"
        
        for i, header in enumerate(headers):
            self.cell(col_width[i], 7, header, 1, fill=True) # set fill=True to use the fill color
        self.ln()
        # Resetting text color back to black for items
        self.set_text_color(0, 0, 0)
        # items
        for item in items:
            for i, value in enumerate(item):
                self.cell(col_width[i], 7, str(value), 1)
            self.ln()

def generate_invoice(customer_info, items, total):
    pdf = PDF(customer_info)
    pdf.add_page(orientation='L')  # Set orientation to Landscape
    pdf.add_invoice_items(items)
    pdf.cell(0, 20, f'Total: ${total}', 0, 0, 'R')
    pdf.output('C:\\Users\\serge\\Desktop\\EDIFY\\invoice.pdf')

# Sample Usage
customer_info = """
AllInWon Med & IT
Valley Cottage, NY 10989
(718) 362-1411
krystal@allinwonmed
"""

items = [
    ["Updates/Maintenance", "a111", "Update and maintenance", "$1,000.00", "$1,000.00"],
]

generate_invoice(customer_info, items, "1,000.00")
