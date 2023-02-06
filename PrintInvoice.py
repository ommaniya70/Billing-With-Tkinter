import jinja2
import pdfkit
import pandas as pd  

def CreatePDF():

    df = pd.read_excel('temp.xlsx')
    records = df.set_index('Sr. No.').T.to_dict('list')
    template_loader = jinja2.FileSystemLoader(searchpath='./')
    template_env = jinja2.Environment(loader=template_loader)
    template_file = 'index.html'
    template = template_env.get_template(template_file)
    output_text = template.render({'data' : records})
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_path = 'Invoice.pdf'  
    html_path = "temp.html"
    html_file = open(html_path, 'w')
    html_file.write(output_text)
    html_file.close()
    print(f"Now converting... ")
    pdfkit.from_string(output_text, pdf_path, configuration=config)