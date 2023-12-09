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
    ws['A1'] = "Results"
    ws['B1'] = "HTML / Link Before"
    ws['C1'] = "HTML / Link After"
    ws['D1'] = "Tries"
    ws['G1'] = "Links with Intercept Errors:"
    ws['H1'] = "Links with Timeout Errors:"
    ws['I1'] = "Links with Not Interactable Exception:"
    ws['J1'] = "Links could not be scanned:"
    ws['K1'] = "Links with Stale Element:"
    ws['K1'] = "Links with unknown Errors:"
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

    elif len(data) == 2:
        ws[f'A{row}'] = data[0]
        ws[f'B{row}'] = data[1]

    else:
        ws[f'A{row}'] = data[0]                       #result
        ws[f'B{row}'] = data[1]                       #before
        ws[f'C{row}'] = data[2]                       #after
        ws[f'D{row}'] = f'Tries: {data[3]}'           #number of Tries
        # ws[f'E{row}'] = f'{data[4]}'
    row += 1
    wb.save("TESTING.xlsx")

initialize()