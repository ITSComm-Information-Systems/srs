from project.pinnmodels import UmEcommMbidWarehseInput, UmEcommMbidCriticalDate, UmEcommMbidVendorInput, UmEcommMbidCommodityV, UmEcommMbidVendorV, UmBomProcurementUsersV

# Url
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect, reverse

# Functional
from apps.mbid.forms import createCycle
import csv
import math
import time
import threading
from io import StringIO
from datetime import date, datetime
from django.core.mail import EmailMessage
from django.db import connections
from django.db.models import Q

# Security
from django.views.decorators.http import condition
from django.contrib.auth.decorators import login_required, permission_required

# Required information for most pages
convert = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
           '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
reverse_convert = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                   'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'}

# Call on views that display or use cycle information


def cycle():
    cycle_info = {'open': False, 'viewable': False}
    try:
        current_cycle = UmEcommMbidCriticalDate.objects.get(bidding_closed='O')
        cycle_info['current_year'] = current_cycle.bidding_year
        cycle_info['current_month_num'] = current_cycle.bidding_month
        cycle_info['current_month'] = convert[current_cycle.bidding_month]

        cycle_info['current_open_date'] = datetime.strptime(
            str(current_cycle.bidding_open_date), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
        cycle_info['current_close_date'] = datetime.strptime(
            str(current_cycle.bidding_close_date), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
        if current_cycle.bidding_close_time < datetime.now():
            current_cycle.bidding_closed = 'C'
            current_cycle.save()
            cycle_info['viewable'] = True
        else:
            cycle_info['open'] = True
    except:
        try:
            current_cycle = UmEcommMbidCriticalDate.objects.get(
                bidding_closed='C')
            cycle_info['current_year'] = current_cycle.bidding_year
            cycle_info['current_month_num'] = current_cycle.bidding_month
            cycle_info['current_month'] = convert[current_cycle.bidding_month]

            cycle_info['current_open_date'] = datetime.strptime(
                str(current_cycle.bidding_open_date), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
            cycle_info['current_close_date'] = datetime.strptime(
                str(current_cycle.bidding_close_date), '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
            cycle_info['viewable'] = True
        except:
            cycle_info['viewable'] = False

    return cycle_info

# All MBid users views


@login_required
def home(request):
    cycle_info = cycle()
    context = {
        'title': 'MBid',
        'cycle_info': cycle_info,
        'procurement': UmBomProcurementUsersV.objects.filter(username=request.user.username.upper(), security_role_code='UM Procurement').exists(),
    }
    return render(request, 'mbid/home.html', context)


@login_required
def faq(request):
    return render(request, 'mbid/faq.html', {'title': 'FAQ'})


def complete(request, message):
    context = {'message': ''}
    if (message == 1):
        cycle_info = cycle()
        context['message'] = "Created Bid Cycle " + \
            cycle_info['current_month']+' '+cycle_info['current_year']
    if (message == 2):
        context['message'] = 'You will be emailed a CSV'
    return render(request, 'mbid/message.html', context)


# Mike-only views
@login_required
@permission_required('mbid_procurement', raise_exception=True)
def create_cycle(request):
    cycles = []
    for item in UmEcommMbidCriticalDate.objects.all().order_by('-bidding_year', 'bidding_month'):
        month = convert[item.bidding_month]
        cycles.append(str(month)+' '+str(item.bidding_year))

    if (request.method == 'POST') and (request.POST.get('infopage') == 'Done'):
        return redirect('complete/1')

    if (request.method == 'POST') and (request.POST.get('makeCycle') == 'Create'):
        openDateTime = request.POST.get('openDate')+' 00:00:00'
        closeDateTime = request.POST.get('closeDate')+' 23:59:59'

        UmEcommMbidCriticalDate.objects.create(bidding_open_date=openDateTime,
                                               bidding_open_time=openDateTime,
                                               bidding_close_date=closeDateTime,
                                               bidding_close_time=closeDateTime,
                                               bidding_closed='O',
                                               bidding_year=request.POST.get(
                                                   'bidYear'),
                                               bidding_month=reverse_convert[request.POST.get(
                                                   'bidMonth')],
                                               date_created=datetime.now().strftime("%Y-%m-%d %H:%M"),
                                               date_last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"))

        run_proc()
        rows = []
        datalist = UmEcommMbidWarehseInput.objects.filter(bidding_closed='O')
        for data in datalist:
            umcode = data.item_code
            desc = data.item_desc
            bid_status = data.bid_status
            req_qty = data.qty_required
            annual_qty = data.annual_qty
            um_notes = data.um_notes

            data = {'umcode': umcode, 'desc': desc,
                    'req_qty': req_qty, 'annual_qty': annual_qty, 'bid_status': bid_status, 'um_notes': um_notes}
            rows.append(data)

        return render(request, 'mbid/a_createCycle.html', {
            'title': 'Create New Bid Cycle',
            'subtitle': 'Review:',
            'bidYear': request.POST.get('bidYear'),
            'bidMonth': request.POST.get('bidMonth'),
            'openDate': datetime.strptime(request.POST.get('openDate'), '%Y-%m-%d').strftime('%B %d, %Y'),
            'closeDate': datetime.strptime(request.POST.get('closeDate'), '%Y-%m-%d').strftime('%B %d, %Y'),
            'rows': rows,
            'totalItems': len(rows),
            'confirm': True,
        })
    else:

        form = createCycle()
        return render(request, 'mbid/a_createCycle.html', {
            'form': form,
            'title': 'Create New Bid Cycle',
            'create': True,
            'cycles': cycles
        })


@login_required
@permission_required('mbid_procurement', raise_exception=True)
def edit_cycle(request):
    cycles = []
    form = createCycle()
    cycle_info = cycle()
    for item in UmEcommMbidCriticalDate.objects.all().order_by('-bidding_year', 'bidding_month'):
        if item.bidding_closed == 'C':
            status = 'Closed'
        elif item.bidding_closed == 'O':
            status = 'Open/Current'
        else:
            status = 'Archived'
        month = convert[item.bidding_month]
        cycles.append({'year': item.bidding_year, 'month': month, 'info': str(
            item.bidding_month)+' '+str(item.bidding_year), 'status': status})

    if (request.method == 'POST'):
        target = request.POST.get('info').split()
        month = target[0]
        year = target[1]
        result = UmEcommMbidCriticalDate.objects.get(
            bidding_month=month, bidding_year=year)
        if request.POST.get('cycleAction') == 'edit':
            oldOpenDate = result.bidding_open_date.strftime("%Y-%m-%d")
            oldCloseDate = result.bidding_close_date.strftime("%Y-%m-%d")
            newOpenDate = request.POST.get('newOpenDate')
            newCloseDate = request.POST.get('newCloseDate')

            if (newOpenDate != ''):
                result.bidding_open_time = newOpenDate+' 00:00:00'
                result.bidding_open_date = newOpenDate+' 00:00:00'
                result.save()
            elif (newOpenDate == ''):
                newOpenDate = oldOpenDate
            if (newCloseDate != ''):
                result.bidding_close_time = newCloseDate+' 23:59:59'
                result.bidding_close_date = newCloseDate+' 23:59:59'
                result.save()
            elif (newCloseDate == ''):
                newCloseDate = oldCloseDate
            message = "Bid Cycle dates changed."
        elif request.POST.get('cycleAction') == 'close':
            result.bidding_closed = 'C'
            result.bidding_close_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            result.bidding_close_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            result.save()
            message = 'Bidding cycle {} {} has been closed.'.format(
                convert[month], str(year))
            run_proc()
            UmEcommMbidVendorInput.objects.filter(
                bidding_month=month, bidding_year=year).update(bidding_closed='C')

        elif request.POST.get('cycleAction') == 'archive':
            result.bidding_closed = 'A'
            result.date_last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
            result.save()
            message = 'Bidding cycle {} {} has been archived.'.format(
                convert[month], str(year))
            run_proc()
            UmEcommMbidVendorInput.objects.filter(
                bidding_month=month, bidding_year=year).update(bidding_closed='A')

        return render(request, 'mbid/message.html', context={'message': message})

    rows = []
    if (cycle_info['open'] == True):
        datalist = UmEcommMbidWarehseInput.objects.filter(bidding_closed='O')
        for data in datalist:
            umcode = data.item_code
            desc = data.item_desc
            bid_status = data.bid_status
            req_qty = data.qty_required
            annual_qty = data.annual_qty
            um_notes = data.um_notes

            data = {'umcode': umcode, 'desc': desc,
                    'req_qty': req_qty, 'annual_qty': annual_qty, 'bid_status': bid_status, 'um_notes': um_notes}
            rows.append(data)

    return render(request, 'mbid/a_editCycle.html', {
        'title': 'Edit Bid Cycle',
        'cycles': cycles,
        'cycle_info': cycle_info,
        'rows': rows,
        'totalItems': len(rows)
    })


@login_required
@permission_required('mbid_procurement', raise_exception=True)
def review(request):
    # Get available cycles
    cycles = []
    for item in UmEcommMbidCriticalDate.objects.all().order_by('-bidding_year', 'bidding_month'):
        if item.bidding_closed == 'C':
            status = 'Closed'
        elif item.bidding_closed == 'A':
            status = 'Archived'
        elif item.bidding_closed == 'O':
            status = 'Open'
        else:
            status = 'idk what '+str(item.bidding_closed)+' means'
        month = convert[item.bidding_month]
        cycles.append((item.bidding_year, month, status, item.bidding_month))

    if request.method == 'POST':
        thread = threading.Thread(
            target=create_mike_report, args=(request,))
        thread.start()
        return redirect('complete/2')
        
    return render(request, 'mbid/a_reviewBids.html', {'title': 'Review Bid Cycles', 'cycles': cycles})


# Vendor-only views
@login_required
@permission_required('is_vendor', raise_exception=True)
def create_cycle_report(request):
    cycle_info = cycle()
    if (cycle_info['open'] == True):
        # Use CommodityV because it's supposed to pull from current cycle
        # and includes manufacturer_part_number
        datalist = UmEcommMbidCommodityV.objects.filter(
            bidding_year=cycle_info['current_year']).order_by('manufacturer_id')
    else:
        return render(request, 'mbid/message.html', {'message': 'The bid cycle is closed and you may not place bids.'})

    rows = []

    # CSV prep that is also pulling the 'preview' data
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="MBid_' + \
        str(cycle_info['current_month'])+'_' + \
        str(cycle_info['current_year'])+'.csv"'

    fieldnames = ['Manufacturer', 'UM Code', 'Manufacturer Part Number', 'Description', 'Bid Status',
                  'Required QTY @ Local Vendor Branch', 'Estimated Annual Qty', 'Unit of Measure', 'UM Notes', 'Vendor Notes', 'Bid Price']
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for data in datalist:
        mfr = data.manufacturer_id
        umcode = data.item_code
        desc = data.title
        manufacturer_part_number = data.manufacturer_part_number
        bid_status = data.bid_status
        req_qty = data.qty_required
        annual_qty = data.annual_qty
        uom = data.uom
        um_notes = data.um_notes
        rows.append({'mfr': mfr, 'umcode': umcode, 'manufacturer_part_number': manufacturer_part_number, 'desc': desc, 'bid_status': bid_status,
                     'req_qty': req_qty, 'annual_qty': annual_qty, 'uom': uom, 'um_notes': um_notes})
        writer.writerow(
            {'Manufacturer': mfr, 'UM Code': umcode, 'Manufacturer Part Number': manufacturer_part_number, 'Description': desc, 'Bid Status': bid_status, 'Required QTY @ Local Vendor Branch': req_qty, 'Estimated Annual Qty': annual_qty, 'Unit of Measure': uom, 'UM Notes': um_notes, 'Vendor Notes': '', 'Bid Price': ''})

    if request.method == 'POST':
        return response

    context = {
        'title': 'Create Report',
        'rows': rows,
        'totalItems': len(rows),
        'cycle_info': cycle_info
    }
    return render(request, 'mbid/c_cycleExport.html', context)


@login_required
@permission_required('is_vendor', raise_exception=True)
def upload_bids(request):
    # Two parts to this view
    # 1. allowing vendors to upload
    # 2. reviewing the vendor upload before submitting to databse
    cycle_info = cycle()
    context = {'title': 'Upload Bids', 'cycle_info': cycle_info}
    try: # No matter who it is you NEED to be in the vendor table to upload
        vendor = UmEcommMbidVendorV.objects.get(
            email_address=request.user.email)
    except:
        return render(request, 'mbid/message.html', {'message': 'You do not have permission to view this'})

    # Vendor bids get uploaded if there is an open cycle, and the datetime is within the bid cycle
    if (request.method == "POST") and (UmEcommMbidCriticalDate.objects.filter(bidding_closed='O').exists()) and (datetime.now() > UmEcommMbidCriticalDate.objects.get(bidding_closed='O').bidding_open_time) and (datetime.now() < UmEcommMbidCriticalDate.objects.get(bidding_closed='O').bidding_close_time) and (request.POST.get('uploadstatus') == 'Upload Bids'):
        file = request.FILES['csv_file']
        decoded_file = file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        valid = []
        notvalid = []
        old = ['Manufacturer', 'UM Code', 'Manufacturer Part Number', 'Description', 'Bid Status', 'Required QTY @ Local Vendor Branch',
               'Estimated Annual Qty', 'Unit of Measure', 'UM Notes', 'Vendor Notes', 'Bid Price']
        new = ['Manufacturer', 'UMCode', 'ManufacturerPartNumber', 'Description', 'BidStatus', 'RequiredQTY',
               'AnnualQty', 'UnitofMeasure', 'UMNotes', 'VendorNotes', 'BidPrice']
        for row in reader:
            # DictReader returns as OrderedDict, fix that.
            row = dict(row)
            for o, n in zip(old, new):
                row[n] = row.pop(o)
            # If valid price
            if (pricecheck(row['BidPrice']) != None) and (pricecheck(row['BidPrice']) != False):
                valid.append(row)
            # If empty and vendor notes
            elif (pricecheck(row['BidPrice']) == None) and (row['VendorNotes'] != ''):
                notvalid.append(row)
            elif (pricecheck(row['BidPrice']) == False):  # If invalid price
                notvalid.append(row)
            else:
                pass

        mistakes = False
        if (notvalid != []):
            mistakes = True
        context = {'valid': valid, 'mistakes': mistakes,
                   'notvalid': notvalid, 'title': 'Uploaded Bids'}

        return render(request, 'mbid/c_checkLoad.html', context)
    elif (request.method == 'POST') and (request.POST.get('uploadstatus') == 'Submit Bids'):
        thread = threading.Thread(target=update_vendor_table, args=(request,))
        thread.start()
        # EDIT MESSAGE 
        return render(request, 'mbid/message.html', {'title': 'Upload Bids', 'message': 'Your bids are being uploaded.'})
    return render(request, 'mbid/c_uploadBids.html', context)


@login_required
@permission_required('is_vendor', raise_exception=True)
def review_bids(request):
    cycle_info = cycle()
    if (cycle_info['open'] == True) or (cycle_info['viewable'] == True):
        try:
            inputlist = UmEcommMbidVendorInput.objects.filter(
                bidding_year=cycle_info['current_year'],
                bidding_month=cycle_info['current_month_num'],
                vendor_id=UmEcommMbidVendorV.objects.get(email_address=request.user.email).id)
        except:
            return render(request, 'mbid/message.html', {'message': 'Vendor not found'})

    else:
        return render(request, 'mbid/message.html', {'message': 'The bid cycle is closed and you can no longer view your bids.'})

    rows = []

    for item in inputlist:
        extra = UmEcommMbidCommodityV.objects.get(
            bidding_year=cycle_info['current_year'], bidding_month=cycle_info['current_month_num'], item_code=item.item_code)

        manufacturer_name = item.manufacturer_name
        umcode = item.item_code
        desc = item.item_desc
        vendor_notes = item.vendor_notes
        price = item.vendor_price
        manufacturer_part_number = item.manufacturer_part_number
        uom = extra.uom
        req_qty = extra.qty_required
        annual_qty = extra.annual_qty
        bid_status = extra.bid_status
        um_notes = extra.um_notes

        data = {'manufacturer_name': manufacturer_name, 'umcode': umcode, 'desc': desc, 'manufacturer_part_number': manufacturer_part_number, 'bid_status': bid_status,
                'um_notes': um_notes, 'uom': uom, 'req_qty': req_qty, 'annual_qty': annual_qty, 'vendor_notes': vendor_notes, 'price': price}
        rows.append(data)

    context = {
        'title': 'Review Bids',
        'rows': [],
        'rows': rows,
        'totalItems': len(rows),
        'noitems': (len(rows) == 0),
        'cycle_info': cycle_info
    }
    return render(request, 'mbid/c_cycleReport.html', context)

# Not views

def pricecheck(bidprice):
    # return None if can't be converted/empty
    # return False if invalid
    if (bidprice == ''):
        return None
    try:
        num = float(bidprice)  # can error here if invalid string
        if (num > 0) and (num == round(num, 2)):
            return num
        elif (num == 0):
            return 'zero'
        else:
            return False
    except:
        return False


def run_proc():
    curr = connections['pinnacle'].cursor()
    try:
        curr.callproc(
            'UM_VENDOR_BIDDING_INTERFACE_K.UM_UPDATE_WAREHSE_INPUT_P')
    except:
        print('error')
    curr.close()

# # Send emails via thread

def update_vendor_table(request):
    cycle_info = cycle()
    post = request.POST
    vendor = UmEcommMbidVendorV.objects.get(email_address=request.user.email)
    vendor_id = vendor.id
    vendor_name = vendor.name
    vendor_address1 = vendor.address1
    vendor_address2 = vendor.address2
    vendor_city = vendor.city
    vendor_state = vendor.state
    vendor_zip_code = vendor.zip_code  # no zip extension
    vendor_email_address = vendor.email_address
    havetarget = False
    for string in post.getlist('uploads'):
        row = dict({x.split(':')[0]: x.split(':')[1]
                    for x in [item for item in string.split(';')]})
        try:
            target = UmEcommMbidVendorInput.objects.get(
                bidding_year=cycle_info['current_year'], bidding_month=cycle_info['current_month_num'], vendor_id=vendor_id, item_code=row['UMCode'])
            havetarget = True
        except:
            if (float(row['BidPrice']) != 0):
                UmEcommMbidVendorInput.objects.create(
                    bidding_year=cycle_info['current_year'],
                    bidding_month=cycle_info['current_month_num'],
                    bidding_closed='O',
                    item_code=row['UMCode'],
                    item_desc=row['Description'],
                    subclass_id=UmEcommMbidCommodityV.objects.get(
                        item_code=row['UMCode']).subclass_id,
                    manufacturer_name=row['Manufacturer'],
                    manufacturer_part_number=row['ManufacturerPartNumber'],
                    vendor_id=vendor_id,
                    vendor_name=vendor_name,
                    vendor_email_address=vendor_email_address,
                    vendor_address1=vendor_address1,
                    vendor_address2=vendor_address2,
                    vendor_city=vendor_city,
                    vendor_state=vendor_state,
                    vendor_zip_code=vendor_zip_code,
                    vendor_price=float(row['BidPrice']),
                    vendor_notes=str(row['VendorNotes']),
                    date_created=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    date_last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"))
            # print('added item '+ row['UMCode'])
        if havetarget:
            toupdate = UmEcommMbidVendorInput.objects.filter(
                bidding_year=cycle_info['current_year'], bidding_month=cycle_info['current_month_num'], vendor_id=vendor_id, item_code=row['UMCode'])
            if (row['BidPrice'] == '0'):
                target.delete()
                # print('deleted ', row['UMCode'])
            elif ((float(target.vendor_price) != float(row['BidPrice'])) or (str(target.vendor_notes) != str(row['VendorNotes']))):
                toupdate.update(date_last_updated=datetime.now().strftime(
                    "%Y-%m-%d %H:%M"), vendor_price=float(row['BidPrice']), vendor_notes=str(row['VendorNotes']))
                # print('edited ', row['UMCode'])
            else:
                print('no change')

    email = EmailMessage(
        subject='MBid Update',
        body='Your bids were uploaded',
        from_email='srs@umich.edu',
        to=[request.user.email],
    )
    email.send()

def create_mike_report(request):
    # Make sure post is a dictionary
    print(request)
    post = request.POST.dict()
    print(post)
    # Ready email
    email = EmailMessage(
        subject='MBid CSV Report',
        body='See attached CSV',
        from_email='srs@umich.edu',
        to=[request.user.email],)

    # Filter information
    yearmonth = post['pickCycle'].split()
    bidding_month = yearmonth[0]
    bidding_year = yearmonth[1]
    # Set up CSV
    target_csv = StringIO()

    # Retrieve data as specified by selected option
    # If no vendor notes or bids for noBids option
    if (post['downloadOption'] == 'noBids'):
        # Set up CSV
        fieldnames = ['U-M Code', 'Description', 'Bid Status', 'UM Notes']
        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get data
        havebids = set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True))
        rows = UmEcommMbidWarehseInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).exclude(item_code__in=havebids)
        # Write data to csv
        for row in rows:
            writer.writerow({'U-M Code': row.item_code, 'Description': row.item_desc,
                             'Bid Status': row.bid_status, 'UM Notes': row.um_notes})
        email.attach('MikeReport_' + str(bidding_month)+'_'+str(bidding_year) +
                     '_noBids.csv', target_csv.getvalue(), 'text/csv')

    elif (post['downloadOption'] == 'allBids'):
        # Set up CSV
        fieldnames = ['U-M Code', 'Description', 'Bid Status']
        # Get all vendors in bid cycle for header
        for vendor in set(UmEcommMbidVendorInput.objects.filter(bidding_year=bidding_year,bidding_month=bidding_month).values_list('vendor_id', flat=True)):
            fieldnames.extend([vendor + ' Notes', vendor + ' Bids'])

        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get list of UM Codes with bids
        item_codes_list = sorted(set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True)))

        # Write to CSV
        for item in item_codes_list:
            info = UmEcommMbidWarehseInput.objects.get(
                item_code=item, bidding_year=bidding_year, bidding_month=bidding_month)
            towrite = {'U-M Code': item, 'Description': info.item_desc,
                       'Bid Status': info.bid_status}

            results = UmEcommMbidVendorInput.objects.filter(
                bidding_year=bidding_year, bidding_month=bidding_month, item_code=item)
            for row in results:
                towrite[row.vendor_id+' Notes'] = row.vendor_notes
                towrite[row.vendor_id + ' Bids'] = row.vendor_price

            writer.writerow(towrite)

        email.attach('MikeReport_' + str(bidding_month)+'_'+str(bidding_year) +
                     '_allBids.csv', target_csv.getvalue(), 'text/csv')

    elif post.get('downloadOption') == 'lowBids':
        # Set up CSV, 3 lowest bidders
        fieldnames = ['U-M Code', 'Description', 'Bid Status', 'Vendor 1', 'Vendor Notes 1', 'Vendor Price 1',
                      'Vendor 2', 'Vendor Notes 2', 'Vendor Price 2', 'Vendor 3', 'Vendor Notes 3', 'Vendor Price 3']
        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get list of UM Codes with bids
        item_codes_list = sorted(set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True)))

        # Write to CSV
        for item in item_codes_list:
            results = UmEcommMbidVendorInput.objects.filter(
                bidding_year=bidding_year, bidding_month=bidding_month, item_code=item).order_by('vendor_price')[:2]
            info = UmEcommMbidWarehseInput.objects.get(
                item_code=item, bidding_year=bidding_year, bidding_month=bidding_month)
            towrite = {'U-M Code': item, 'Description': info.item_desc,
                       'Bid Status': info.bid_status}  # Basic
            if len(results) == 3:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price
                towrite['Vendor 2'] = results[1].vendor_id
                towrite['Vendor Notes 2'] = results[1].vendor_notes
                towrite['Vendor Price 2'] = results[1].vendor_price
                towrite['Vendor 3'] = results[2].vendor_id
                towrite['Vendor Notes 3'] = results[2].vendor_notes
                towrite['Vendor Price 3':] = [2].vendor_price
            elif len(results) == 2:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price
                towrite['Vendor 2'] = results[1].vendor_id
                towrite['Vendor Notes 2'] = results[1].vendor_notes
                towrite['Vendor Price 2'] = results[1].vendor_price
            elif len(results) == 1:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price

            write.writerow(towrite)

        email.attach('MikeReport_' + str(bidding_month)+'_'+str(bidding_year) +
                     '_lowestBids.csv', target_csv.getvalue(), 'text/csv')

    # Everything written and attached in if statements. Send email.
    email.send(fail_silently=False)


# # For testing purposes when making MikeReports
def direct_download(request):
    # convert to dictionary as with email version
    post = request.POST.dict()

    # Filter information
    yearmonth = post['pickCycle'].split()
    bidding_month = yearmonth[0]
    bidding_year = yearmonth[1]
    # Set up CSV
    target_csv = HttpResponse(content_type='text/csv')
    if (post['downloadOption'] == 'noBids'):
        # Set up CSV
        target_csv['Content-Disposition'] = 'attachment; filename="MikeReport_' + \
            str(bidding_month)+'_'+str(bidding_year)+'_noBids.csv"'
        fieldnames = ['U-M Code', 'Description', 'Bid Status', 'UM Notes']
        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get data
        havebids = set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True))
        rows = UmEcommMbidWarehseInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).exclude(item_code__in=havebids)

        # Write data to csv
        for row in rows:
            writer.writerow({'U-M Code': row.item_code, 'Description': row.item_desc,
                                'Bid Status': row.bid_status, 'UM Notes': row.um_notes})
        return target_csv

    elif (post['downloadOption'] == 'allBids'):
        # Set up CSV
        target_csv['Content-Disposition'] = 'attachment; filename="MikeReport_' + \
            str(bidding_month)+'_'+str(bidding_year)+'_allBids.csv"'
        fieldnames = ['U-M Code', 'Description', 'Bid Status']
        # Get all vendors in bid cycle for header
        for vendor in set(UmEcommMbidVendorInput.objects.filter(bidding_year=bidding_year,bidding_month=bidding_month).values_list('vendor_id', flat=True)):
            fieldnames.extend(
                [vendor + ' Notes', vendor + ' Bids'])

        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get list of UM Codes with bids
        item_codes_list = sorted(set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True)))

        # Write to CSV
        for item in item_codes_list:
            info = UmEcommMbidWarehseInput.objects.get(
                item_code=item, bidding_year=bidding_year, bidding_month=bidding_month)
            towrite = {
                'U-M Code': item, 'Description': info.item_desc, 'Bid Status': info.bid_status}

            results = UmEcommMbidVendorInput.objects.filter(
                bidding_year=bidding_year, bidding_month=bidding_month, item_code=item)
            for row in results:
                towrite[row.vendor_id+' Notes'] = row.vendor_notes
                towrite[row.vendor_id + ' Bids'] = row.vendor_price

            writer.writerow(towrite)

        return target_csv

    elif post.get('downloadOption') == 'lowBids':
        # Set up CSV, 3 lowest bidders
        target_csv['Content-Disposition'] = 'attachment; filename="MikeReport_' + \
            str(bidding_month)+'_'+str(bidding_year)+'_lowBids.csv"'
        fieldnames = ['U-M Code', 'Description', 'Bid Status', 'Vendor 1', 'Vendor Notes 1', 'Vendor Price 1',
                        'Vendor 2', 'Vendor Notes 2', 'Vendor Price 2', 'Vendor 3', 'Vendor Notes 3', 'Vendor Price 3']
        writer = csv.DictWriter(target_csv, fieldnames=fieldnames)
        # Header
        writer.writeheader()

        # Get list of UM Codes with bids
        item_codes_list = sorted(set(UmEcommMbidVendorInput.objects.filter(
            bidding_year=bidding_year, bidding_month=bidding_month).values_list('item_code', flat=True)))

        # Write to CSV
        for item in item_codes_list:
            results = UmEcommMbidVendorInput.objects.filter(
                bidding_year=bidding_year, bidding_month=bidding_month, item_code=item).order_by('vendor_price')[:2]
            info = UmEcommMbidWarehseInput.objects.get(
                item_code=item, bidding_year=bidding_year, bidding_month=bidding_month)
            towrite = {'U-M Code': item, 'Description': info.item_desc,
                        'Bid Status': info.bid_status}  # Basic
            if len(results) == 3:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price
                towrite['Vendor 2'] = results[1].vendor_id
                towrite['Vendor Notes 2'] = results[1].vendor_notes
                towrite['Vendor Price 2'] = results[1].vendor_price
                towrite['Vendor 3'] = results[2].vendor_id
                towrite['Vendor Notes 3'] = results[2].vendor_notes
                towrite['Vendor Price 3':] = [2].vendor_price
            elif len(results) == 2:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price
                towrite['Vendor 2'] = results[1].vendor_id
                towrite['Vendor Notes 2'] = results[1].vendor_notes
                towrite['Vendor Price 2'] = results[1].vendor_price
            elif len(results) == 1:
                towrite['Vendor 1'] = results[0].vendor_id
                towrite['Vendor Notes 1'] = results[0].vendor_notes
                towrite['Vendor Price 1'] = results[0].vendor_price

            writer.writerow(towrite)
        return target_csv