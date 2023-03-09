import io
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from .models import Estimate

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing,Line
from .models import Material
from django.db.models import Sum

# Estimate.get_details()

PAGE_SIZE = (8.5 * inch, 11 * inch)
BASE_MARGIN = 0.25 * inch
RIGHT = ParagraphStyle(name="right", alignment=TA_RIGHT)
CENTER = ParagraphStyle(name="center", alignment=TA_CENTER)

class PdfCreator:
	


	def add_page_number(self, canvas, doc):
		canvas.saveState()
		canvas.setFont('Times-Roman', 10)
		page_number_text = "%d" % (doc.page)
		canvas.drawCentredString(
			4.25 * inch,
			0.25 * inch,
			page_number_text
		)
		canvas.restoreState()
	
	def add_page_number_landscape(self, canvas, doc):
		canvas.saveState()
		canvas.setFont('Times-Roman', 10)
		page_number_text = "%d" % (doc.page)
		canvas.drawCentredString(
			5.5 * inch,
			0.25 * inch,
			page_number_text
		)
		canvas.restoreState()


	def get_body_style(self):
		sample_style_sheet = getSampleStyleSheet()
		body_style = sample_style_sheet['BodyText']
		body_style.fontSize = 12
		return body_style


	def get_header_style(self):
		sample_style_sheet = getSampleStyleSheet()
		header_style = sample_style_sheet['Heading1']
		header_style.alignment = 1
		return header_style

	def get_subheader_style(self):
		sample_style_sheet = getSampleStyleSheet()
		header_style = sample_style_sheet['Heading2']
		return header_style

	def get_location_total_style(self):
		header_style = ParagraphStyle(name="right", alignment=TA_RIGHT)
		header_style.fontName='Helvetica-Bold'
		return header_style

	def location_totals(self):
		totals = {}	
		for material in self.estimate.material_list:
			location = material.material_location
			if location not in totals:
				totals[location] = material.extended_price
			else:
				totals[location] += material.extended_price
		return totals

	def build_pdf(self):
		pdf_buffer = io.BytesIO()

		if self.type == 'checkout_list':
			my_doc = SimpleDocTemplate(
			pdf_buffer,
			title='bom_' + self.type + '_report_' + str(self.estimate_id),
			pagesize=(11 * inch, 8.5 * inch),
			topMargin=BASE_MARGIN,
			leftMargin=BASE_MARGIN,
			rightMargin=BASE_MARGIN,
			bottomMargin=0.5 * inch
			)
			flowables = self.get_checkout_list_flowables()
			my_doc.build(
				flowables,
				onFirstPage=self.add_page_number_landscape,
				onLaterPages=self.add_page_number_landscape,
			)

		else:
			my_doc = SimpleDocTemplate(
				pdf_buffer,
				title='bom_' + self.type + '_report_' + str(self.estimate_id),
				pagesize=PAGE_SIZE,
				topMargin=BASE_MARGIN,
				leftMargin=BASE_MARGIN,
				rightMargin=BASE_MARGIN,
				bottomMargin=0.5 * inch
			)

			if self.type == 'location':
				flowables = self.get_location_flowables()
				
			elif self.type == 'summary':
				flowables = self.get_summary_flowables()

			my_doc.build(
				flowables,
				onFirstPage=self.add_page_number,
				onLaterPages=self.add_page_number,
			)
		pdf_value = pdf_buffer.getvalue()
		pdf_buffer.close()
		
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'filename="bom_' + self.type + '_report_' + str(self.estimate_id) + '.pdf"'
		
		response.write(pdf_value)
		return response


	def build_table(self, data, col_widths):
			table = Table(data, colWidths=col_widths)
			table.hAlign = 'LEFT'
			table.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
										('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
			return table


	def build_header(self, normal):
		flowables = []

		# Create project overview table
		data = [[Paragraph('<b>Project</b>', normal), 
				Paragraph('<b>Pre-Order</b>', normal), Paragraph('<b>Work Order</b>', normal),
				Paragraph('<b>Estimate</b>', normal), Paragraph('', normal),
				Paragraph('<b>Building #</b>', normal), Paragraph('<b>Building Name</b>', normal)]]

		if self.estimate.workorder:
			data.append([Paragraph(str(self.estimate.workorder.project_code_display), normal),
						Paragraph(str(self.estimate.workorder.pre_order_number), normal),  
						Paragraph(str(self.estimate.workorder.wo_number_display), normal),
						Paragraph(str(self.estimate.label), normal),
						Paragraph('', normal),
						Paragraph(str(self.estimate.workorder.add_info_list_value_code_1), normal), 
						Paragraph(str(self.estimate.workorder.add_info_list_value_name_1), normal)])
 
		col_widths = [1 * inch, 1 * inch, 1 * inch, 1 * inch, .9 * inch, 0.9 * inch, 2 * inch]
		table = Table(data, colWidths=col_widths)
		table.hAlign = 'LEFT'
		table.setStyle(TableStyle([('INNERGRID', (0,0), (3,2), 0.25, colors.black),
									('INNERGRID', (5,0), (6,1), 0.25, colors.black),
									('BOX', (0,0), (3,2), 0.25, colors.black),
									('BOX', (5,0), (6, 1), 0.25, colors.black)]))
		flowables.append(table)
		flowables.append(Spacer(1, 0.2 * inch))

		# Create department overview table
		data = [[Paragraph('<b>Department Name</b>', normal), Paragraph('<b>Project Engineer</b>', normal), 
				Paragraph('<b>Project Manager</b>', normal)]]
		if self.estimate.workorder:
			data.append([Paragraph(str(self.estimate.workorder.department_name), normal), 
						Paragraph(str(self.estimate.assigned_engineer), normal), 
						Paragraph(str(self.estimate.workorder.add_info_list_value_name_2), normal)])
		col_widths = [1.5 * inch] * 3
		flowables.append(self.build_table(data,col_widths))
		flowables.append(Spacer(1, 0.3 * inch))

		# Add project description
		flowables.append(Paragraph('<b>Project Description:</b>', normal))
		flowables.append(Spacer(1, 0.05 * inch))
		if self.estimate.workorder:
			flowables.append(Paragraph(self.estimate.workorder.comment_text, normal))
		flowables.append(Spacer(1, 0.2 * inch))

		return flowables


	def build_item_summary(self, normal):
		flowables = []

		data = [[Paragraph('<b>Item Code</b>', normal), Paragraph('<b>Item Description</b>', normal),
				Paragraph('<b>Manufacturer Part Number</b>', normal), Paragraph('<b>Quantity</b>', normal),
				Paragraph('<b>Unit Cost</b>', normal), Paragraph('<b>Extension Cost</b>', normal)]]

	# for record in self.estimate.part_list:
	# 		data.append([Paragraph(str(record['item__code']), normal),
	# 					Paragraph(str(record['quantity__sum']), CENTER),
	# 					Paragraph('', normal),
	# 					Paragraph(str(record['item__name']), normal),
	# 					Paragraph(str(record['item__manufacturer_part_number']), normal),
	# 					Paragraph(str(record['release_number']), normal),
	# 					Paragraph(str(record['reel_number']), normal),
	# 					Paragraph(options[str(record['staged'])], normal),
	# 					Paragraph(str(options[record['status']]), normal),
	# 					])

		for record in self.estimate.part_list:
			data.append([Paragraph(str(record['item__code']), normal),
						Paragraph(str(record['item__name']), normal),
						Paragraph(str(record['item__manufacturer_part_number']), normal),
						Paragraph(str(record['quantity__sum']), CENTER),
						Paragraph(str(record['item__price']), normal),
						# Paragraph(f'{record.extended_price:,}', RIGHT)
						])

		col_widths = [1 * inch, 2 * inch, 2 * inch, 0.8 * inch, 0.7 * inch, 1 * inch]
		flowables.append(self.build_table(data, col_widths))
		flowables.append(Spacer(1, 0.2 * inch))
		return flowables


	def build_labor_summary(self, normal):
		flowables = []
		data = [[Paragraph('<b>Department</b>', normal), Paragraph('<b>Labor Description</b>', normal),
				Paragraph('<b>Labor Hours</b>', normal), Paragraph('<b>Hourly Rate</b>', normal),
				Paragraph('<b>Total Labor</b>', normal)]]

		if not self.estimate.labor_list:
			data.append(['', '','0', '0', '0'])

		for record in self.estimate.labor_list:
			data.append([Paragraph(str(record.group), normal),
						Paragraph(str(record.description), normal),
						Paragraph(str(record.hours), CENTER),
						Paragraph(str(record.rate), RIGHT),
						Paragraph(f'{record.extended_cost:,}', RIGHT)])
		col_widths = [2 * inch, 2 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch]
		flowables.append(self.build_table(data, col_widths))
		flowables.append(Spacer(1, 0.2 * inch))
		return flowables


	def build_totals(self, normal):
		flowables = []
		data = [[Paragraph('<b>Labor Hours</b>', normal), Paragraph(str(self.estimate.labor_hours), CENTER)],
				[Paragraph('<b>Labor</b>', normal), Paragraph(f'{self.estimate.labor_total:,}', RIGHT)],
				[Paragraph('<b>Material</b>', normal), Paragraph(f'{self.estimate.material_total:,}', RIGHT)],
				[Paragraph('<b>Contingency Total</b>', normal), Paragraph(f'{self.estimate.contingency_total:,}', RIGHT)],
				[Paragraph('<b>Project Cost</b>', normal), Paragraph(f'{self.estimate.total:,}', RIGHT)]]
		col_widths = [2 * inch, 0.8 * inch]
		flowables.append(self.build_table(data, col_widths))
		return flowables


	def get_location_flowables(self):
		# Table elements
		flowables = [] 

		# Set style
		normal = self.styles['Normal']

		# Create title of page
		title = Paragraph('Bill of Materials By Location', self.header)
		flowables.append(title)
		flowables.append(Spacer(1, 0.2 * inch))

		# Add header to report
		flowables = flowables + self.build_header(normal)

		# Add first location to table
		prev_loc = self.estimate.material_list[0].material_location
		table_heading = [Paragraph('<b>Item Code</b>', normal), Paragraph('<b>Material Detail</b>', normal),
						Paragraph('<b>Manufacturer Part Number</b>', normal), Paragraph('<b>Mfg</b>', normal),
						Paragraph('<b>Est # of Units</b>', normal), Paragraph('<b>Unit Price</b>', normal),
						Paragraph('<b>Price Extension</b>', normal)]
		data = [table_heading]
		flowables.append(Paragraph(str(self.estimate.material_list[0].material_location), self.subheader))
		flowables.append(Paragraph('Total for Location: $' + "{:,}".format(self.location_totals[prev_loc]), self.location_total_style))


		
		# Add materials by location
		for record in self.estimate.material_list:
			# Create new table if location switches
			if record.material_location != prev_loc:
				# Append table to pdf
				col_widths = [0.8 * inch, 2 * inch, 1.7 * inch, 1 * inch, 0.7 * inch, 0.7 * inch, 1 * inch]
				flowables.append(self.build_table(data, col_widths))
				flowables.append(Spacer(1, 0.2 * inch))

				# Create next location title and reset table to just the headings
				flowables.append(Paragraph('<b>' + str(record.material_location) + '</b>', self.subheader))
				flowables.append(Paragraph('Total for Location: $' + "{:,}".format(self.location_totals[record.material_location]), self.location_total_style))
				#str(self.location_totals[record.material_location])
				data = [table_heading]
 
			# Add item to table
			data.append([Paragraph(str(record.item_code), normal),
						Paragraph(str(record.item_description), normal),
						Paragraph(str(record.manufacturer_part_number), normal),
						Paragraph(str(record.manufacturer), normal),
						Paragraph(str(record.quantity), CENTER),
						Paragraph(str(record.price), RIGHT),
						Paragraph(f'{record.extended_price:,}', RIGHT)])

			prev_loc = record.material_location

		# Append final table to page
		col_widths = [0.8 * inch, 2 * inch, 1.7 * inch, 1 * inch, 0.7 * inch, 0.7 * inch, 1 * inch]
		flowables.append(self.build_table(data,col_widths))
		flowables.append(Spacer(1, 0.2 * inch))

		# Create Item Summary
		flowables.append(Paragraph('Item Summary', self.subheader))
		flowables = flowables + self.build_item_summary(normal)

		# Create Labor Summary
		flowables.append(Paragraph('Labor Summary', self.subheader))
		flowables = flowables + self.build_labor_summary(normal)

		# Create simple summary of totals
		flowables.append(Paragraph('Totals', self.subheader))
		flowables = flowables + self.build_totals(normal)

		return flowables


	def get_checkout_list_flowables(self):
		# Table elements
		flowables = [] 

		# Set style
		normal = self.styles['Normal']

		# Create title of page
		title = Paragraph('BOM Checkout List', self.header)
		flowables.append(title)
		flowables.append(Spacer(1, 0.2 * inch))

		# Add info table
		d = Drawing(100, 1)
		d.add(Line(0, 0, 150, 0))
		style = ParagraphStyle(name="myStyle", alignment=TA_RIGHT)
		data = [[Paragraph('<b>Project</b>', normal), Paragraph('<b>Work Order</b>', normal),
				'', Paragraph('<b>Check Out Date</b>', style), d],
				[Paragraph(str(self.estimate.workorder.project_code_display), normal),
				Paragraph(str(self.estimate.workorder.wo_number_display), normal),
				'', Paragraph('<b>Tech Name</b>', style), d]]
		col_widths = [1.3 * inch, 1.3 * inch, 4 * inch, 1.2 * inch, 3 * inch]
		table = Table(data, colWidths=col_widths)
		table.hAlign = 'LEFT'
		table.setStyle(TableStyle([('INNERGRID', (0,0), (1,1), 0.25, colors.black),
									('BOX', (0,0), (1,1), 0.25, colors.black),
									('HALIGN', (0, 0), (-1, -1), 'RIGHT')]))
		flowables.append(table)
		flowables.append(Spacer(1, 0.4 * inch))

		# Add item list
		data = [[Paragraph('<b>Item Number</b>', normal),
				Paragraph('<b>Est Qty</b>', normal),
				Paragraph('<b>Qty</b>', normal),	
				Paragraph('<b>Item Description</b>', normal),
				Paragraph('<b>Manufacturer Number</b>', normal),
				Paragraph('<b>Release Number</b>', normal),
				Paragraph('<b>Reel Number</b>', normal),
				Paragraph('<b>Staged</b>', normal),
				Paragraph('<b>Status</b>', normal)
				]]

		options = {1:'Estimate',2:'In Stock',3:'Ordered', 'True':'Yes','False':'No'}
		
		for record in self.estimate.part_list:
			data.append([Paragraph(str(record['item__code']), normal),
						Paragraph(str(record['quantity__sum']), CENTER),
						Paragraph('', normal),
						Paragraph(str(record['item__name']), normal),
						Paragraph(str(record['item__manufacturer_part_number']), normal),
						Paragraph(str(record['release_number']), normal),
						Paragraph(str(record['reel_number']), normal),
						Paragraph(options[str(record['staged'])], normal),
						Paragraph(str(options[record['status']]), normal),
						])

		col_widths = [1 * inch, .5 * inch, .8 * inch, 3.3 * inch , 1.5 * inch, .7 * inch, .7 * inch, .7 * inch, .8 * inch]
		table = Table(data, colWidths=col_widths)
		table.setStyle(TableStyle([('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
									('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
		flowables.append(table)
		flowables.append(Spacer(1, 0.4 * inch))

		# Provide space to write in additional items
		centered = self.subheader
		centered.alignment = TA_CENTER
		flowables.append(Paragraph('Additional Items Checked Out', self.subheader))
		flowables.append(Spacer(1, 0.1 * inch))
		data = [[Paragraph('<b>Item Number</b>', normal), Paragraph('<b>Estimated Quantity</b>', normal),
				Paragraph('<b>Item Description</b>', normal), Paragraph('<b>Manufacturer Number</b>', normal)]]
		col_widths = [None] * 4
		table = Table(data, col_widths)
		table.hAlign = 'LEFT'
		flowables.append(table)
		flowables.append(Spacer(1, 0.2 * inch))
		for i in range(6):
			d = Drawing(100, 1)
			d.add(Line(0, 0, 700, 0))
			flowables.append(d)
			flowables.append(Spacer(1, 0.2 * inch))

		return flowables


	def get_summary_flowables(self):
		# Table elements
		flowables = [] 

		# Set style
		normal = self.styles['Normal']

		# Create title of page
		title = Paragraph('BOM Summary', self.header)
		flowables.append(title)
		flowables.append(Spacer(1, 0.1 * inch))

		# Add header to report
		flowables = flowables + self.build_header(normal)

		# Add item summary
		flowables = flowables + self.build_item_summary(normal)

		# Add labor summary
		flowables.append(Paragraph('Labor Summary', self.subheader))
		flowables = flowables + self.build_labor_summary(normal)

		# Add totals
		flowables.append(Paragraph('Totals', self.subheader))
		flowables = flowables + self.build_totals(normal)

		return flowables


	def __init__(self, type, estimate_id):
		self.type = type
		self.estimate_id = estimate_id
		self.estimate = get_object_or_404(Estimate, pk=estimate_id)
		self.estimate.get_detail()
		self.styles = getSampleStyleSheet()
		self.body = self.get_body_style()
		self.header = self.get_header_style()
		self.subheader = self.get_subheader_style()
		self.location_total_style = self.get_location_total_style()
		self.location_totals = self.location_totals()


def by_location_report(request, estimate_id):
	pdf = PdfCreator(type='location', estimate_id=estimate_id)
	return pdf.build_pdf()


def checkout_list_report(request, estimate_id):
	pdf = PdfCreator(type='checkout_list', estimate_id=estimate_id)
	return pdf.build_pdf()


def summary_report(request, estimate_id):
	pdf = PdfCreator(type='summary', estimate_id=estimate_id)
	return pdf.build_pdf()

def human_bool(param):
	if param:
		return 'Yes'
	else:
		return 'No'
