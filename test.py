a = [1, 6, 3, 2, 62]
# a.sort()
print(a)


def sort_lists(l1, l2):
    final_lst = []

    p1 = 0
    p2 = 0
    while p1 < len(l1) or p2 < len(l2):

        if p1 < len(l1) and p2 < len(l2):
            if l1[p1] < l2[p2]:
                final_lst.append(l1[p1])
                p1 += 1
            else:
                final_lst.append(l2[p2])
                p2 += 1

        elif p1 < len(l1):
            final_lst.append(l1[p1])
            p1 += 1
        else:
            final_lst.append(l2[p2])
            p2 += 1
    return final_lst


def split_lst(lst):
    if (len(lst) < 2):
        return lst

    high = len(lst)
    low = 0
    mid = (high + low) // 2

    upper = split_lst(lst[low:mid])
    lower = split_lst(lst[mid:high])

    final = sort_lists(upper, lower)
    return final


print(split_lst(a))
