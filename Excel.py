import openpyxl

wb = openpyxl.Workbook()
ws = wb.active

row = 2
intercept_row = 2
timeout_row = 2
other_row = 2
noscan_row = 2
notInteractable_row = 2
(intercept_lst, timeout_lst, notInteractable_lst,
 staleElems_lst, noScan_lst, other_lst) = [[] for i in range(6)]

def initialize():
    ws['A1'] = "Dropdown Opened?"
    ws['B1'] = "Outer HTML Change"
    ws['C1'] = "DOM structure Change"
    ws['D1'] = "Initial Outer HTML "
    ws['E1'] = "After Click Outer HTML"
    ws['F1'] = "Initial DOM Structure"
    ws['G1'] = "After Click DOM Structure"
    ws['H1'] = "Initial Link"
    ws['I1'] = "After Click Link"
    ws['J1'] = "Tries"

    ws['L1'] = "Links with Intercept Errors:"
    ws['M1'] = "Links with Timeout Errors:"
    ws['N1'] = "Links with Not Interactable Exception:"
    ws['O1'] = "Links could not be scanned:"
    ws['P1'] = "Links with Stale Element:"
    ws['Q1'] = "Links with unknown Errors:"
    wb.save("TESTING.xlsx")

def write_intercepts(site):
    global intercept_row
    if site not in intercept_lst:
        intercept_lst.append(site)
        ws[f'G{intercept_row}'] = site
        intercept_row += 1
        wb.save("TESTING.xlsx")


def write_timeout_row(site):
    global timeout_row
    if site not in timeout_lst:
        timeout_lst.append(site)
        ws[f'H{timeout_row}'] = site
        timeout_row += 1
        wb.save("TESTING.xlsx")

def write_notInteractable_row(site):
    global notInteractable_row
    if site not in notInteractable_lst:
        notInteractable_lst.append(site)
        ws[f'I{noscan_row}'] = site
        notInteractable_row += 1
        wb.save("TESTING.xlsx")
def write_noscan_row(site):
    global noscan_row
    if site not in noScan_lst:
        noScan_lst.append(site)
        ws[f'J{noscan_row}'] = site
        noscan_row += 1
        wb.save("TESTING.xlsx")

def write_other_row(site):
    global other_row
    if site not in other_lst:
        other_lst.append(site)
        ws[f'K{other_row}'] = site
        other_row += 1
        wb.save("TESTING.xlsx")


def write_results(data):
    global row

    # Format = ['True redirect', HTML / link Before, HTML / link After, tries, DOM]
    if type(data) is str:
        row += 1
        ws[f'A{row}'] = data                          #website

    else:
        ws[f'A{row}'] = data[0]                       #opened?
        ws[f'B{row}'] = data[1]                       #OuterHTML Change
        ws[f'C{row}'] = data[2]                       #DOM Change
        ws[f'D{row}'] = data[3]                       #InitialOuterHTML
        ws[f'E{row}'] = data[4]                       #AfterClickOuterHTML
        ws[f'F{row}'] = data[5]                       #DOM Initial
        ws[f'G{row}'] = data[6]                       #DOM After Click
        ws[f'H{row}'] = data[7]                       #URL Initial
        ws[f'I{row}'] = data[8]                       #URL AFter
        ws[f'J{row}'] = f'Tries: {data[9]}'           #number of Tries

    row += 1
    wb.save("TESTING.xlsx")

initialize()