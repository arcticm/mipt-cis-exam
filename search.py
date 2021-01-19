# create suffix array

def create_suffix_array(text):
    
    s12_unsorted = create_suffix_one_two(text)

    s12_ranked = bucketsort(text, s12_unsorted)
    s12_ranks = [item[0] for item in s12_ranked]

    if len(set(s12_ranks)) == len(s12_ranks):
        s12 = [item[1] for item in sorted(s12_ranked, key=lambda x: x[0])]
    else:
        sa_s12 = create_suffix_array(s12_ranks)
        s12 = [s12_ranked[id][1] for id in sa_s12]
    s0 = create_suffix_zero(text, s12)
    inversed_suffix_array = create_inverse_suffix_array(len(text), s12)
    merged_suffix_array = merge_suffix_array(text, s0, s12, inversed_suffix_array)

    return merged_suffix_array


# create the inverse suffix array for merging
def create_inverse_suffix_array(len_text, suffix_array):
    inversed = [-1] * len_text
    for i in range(len(suffix_array)):
        inversed[suffix_array[i]] = i

    return inversed

# create suffix array for positions not multiple of 3
def create_suffix_one_two(text):
    # creating the array
    s1 = []
    s2 = []

    # filling the triplet arrays
    for id in range(len(text)):
        if id % 3 == 1:
            s1.append(id)
        elif id % 3 == 2:
            s2.append(id)
    return s1 + s2

# create suffix array for positions multiple of 3
def create_suffix_zero(text, s12):
    #unsorted suffix array
    s0_unsorted = []

    # create the suffix array sorted by the second letter
    for id in s12:
        if ((id - 1) % 3) == 0:
            s0_unsorted.append(id - 1)

    if len(text) % 3 == 1:
        s0_unsorted.insert(0, len(text) - 1)

    # sort the suffix array by the first letter
    s0_sorted= bucketsort(text, s0_unsorted, s0=True)

    # extract the values for suffix array
    s0 = [suf[1] for suf in sorted(s0_sorted, key=lambda suf: suf[0])]
    return s0

# sort s12 suffixes
def bucketsort(text, suffix_array, s0=False):
    triplet_id = 2
    if s0:
        triplet_id = 0
    suffix_array_sorted = suffix_array

    # sort the sa
    for i in range(triplet_id, -1, -1):
        bucket = dict()

        for id in suffix_array_sorted:
            triplet = get_triplet(text, id)
            checked = i if i < len(triplet) else len(triplet) - 1

            if triplet[checked] not in bucket:
                bucket[triplet[checked]] = []

            bucket[triplet[checked]].append(id)

        suffix_array_sorted = []

        for key in sorted(bucket.keys()):
            suffix_array_sorted += bucket[key]

    # get the ranks
    ranks = dict()
    rank = 1

    for text_id in suffix_array_sorted:
        triplet = ''.join([str(item) for item in get_triplet(text, text_id)])
        if triplet not in ranks:
            ranks[triplet] = rank
            rank += 1

    # combine s12 and ranks
    s12_ranked = [(ranks.get(''.join([str(x) for x in get_triplet(text, id)])), id) for id in suffix_array]

    return s12_ranked


def get_triplet(text, id):
    triplet = []
    for text_id in range(id, min(id + 3, len(text))):
        triplet.append(text[text_id])

    while len(triplet) < 3 and isinstance(triplet, str):
        triplet.append("$")

    return triplet


def merge_suffix_array(text, s0, s12, inversed_suffix_array):
    suffix_array = []
    id_s0 = 0
    id_s12 = 0

    while (id_s0 + id_s12) < (len(s0) + len(s12)):

        if id_s0 >= len(s0):
            suffix_array.append(s12[id_s12])
            id_s12 += 1
            continue

        if id_s12 >= len(s12):
            suffix_array.append(s0[id_s0])
            id_s0 += 1
            continue

        cur_s0 = s0[id_s0]
        cur_s12 = s12[id_s12]

        # check for first char
        if text[cur_s0] > text[cur_s12]:
            suffix_array.append(cur_s12)
            id_s12 += 1
            continue

        if text[cur_s0] < text[cur_s12]:
            suffix_array.append(cur_s0)
            id_s0 += 1
            continue

        if text[cur_s0] == text[cur_s12]:

            i = 1
            while True:
                # check with inverse_sa
                if (cur_s0 + i) % 3 == 0 or (cur_s12 + i) % 3 == 0:
                    # check for second char
                    if text[cur_s0 + i] > text[cur_s12 + i]:
                        suffix_array.append(cur_s12)
                        id_s12 += i
                        break

                    if text[cur_s0 + i] < text[cur_s12 + i]:
                        suffix_array.append(cur_s0)
                        id_s0 += i
                        break

                    if text[cur_s0 + i] == text[cur_s12 + i]:
                        i += 1
                        continue
                    continue

                if inversed_suffix_array[cur_s0 + i] > inversed_suffix_array[cur_s12 + i]:
                    suffix_array.append(cur_s12)
                    id_s12 += 1
                    break

                if inversed_suffix_array[cur_s0 + i] < inversed_suffix_array[cur_s12 + i]:
                    suffix_array.append(cur_s0)
                    id_s0 += 1
                    break

    return suffix_array

# generate the left lcp and the right lcp
def precompute_binary_lcp(lcp):
    left_lcp = [None] * (len(lcp))
    right_lcp = [None] * (len(lcp))

    def recursive_binary_lcp(left, right):
        if left == right - 1:
            return lcp[left]
        median = (left + right) // 2
        left_lcp[median] = recursive_binary_lcp(left, median)
        right_lcp[median] = recursive_binary_lcp(median, right)
        return min(left_lcp[median], right_lcp[median])
    recursive_binary_lcp(0, len(lcp))
    return left_lcp, right_lcp


# precompute the longest common prefix
def create_lcp(text, suffix_array, inversed_suffix_array):
    l = 0
    lcp = [0] * len(text)
    for i in range(len(text)):
        k = inversed_suffix_array[i]
        if k + 1 < len(text):
            j = suffix_array[k + 1]
            while text[i + l] == text[j + l]:
                l += 1
            lcp[k] = l
            if l > 0:
                l = l - 1
        else:
            l = 0
            lcp[k] = l

    return lcp


# find one id in the suffix-array where the searchtext matches
def binary_search(t, sa, p, lcp_lr):
    lcp_l = lcp_lr[0]
    lcp_r = lcp_lr[1]

    l = 0
    r = len(sa)
    lcp_pl = 0
    lcp_pr = 0
    while True:
        c = (l + r) // 2
        left_part = True
        compare = False
        i = min(lcp_pl, lcp_pr)

        if lcp_pl > lcp_pr:
            if lcp_l[c] > lcp_pl:
                left_part = False
            elif lcp_l[c] < lcp_pl:
                left_part = True
            elif lcp_l[c] == lcp_pl:
                compare = True

        else:
            if lcp_r[c] > lcp_pr:
                left_part = True
            elif lcp_r[c] < lcp_pr:
                left_part = False
            elif lcp_r[c] == lcp_pr:
                compare = True

        if compare:
            while (i < len(p)) and (sa[c] + i < len(t)):
                if p[i] < t[sa[c] + i]:
                    break

                elif p[i] > t[sa[c] + i] or len(p) <= i:
                    left_part = False
                    break

                elif len(p) > len(t[sa[c]:]):
                    left_part = False
                    break

                i += 1

            if len(p) <= i:
                return c

        if left_part:
            if c == l + 1:
                if i < len(p):
                    return False
                return c

            r = c
            lcp_pr = i

        else:
            if c == r - 1:
                if i < len(p):
                    return False
                return r

            l = c
            lcp_pl = i


# count how often the pattern is in the text
def count_results(suffix_array_id, pattern_length, lcp):
    if not suffix_array_id:
        return 0
    i = suffix_array_id
    count = 1
    while pattern_length <= lcp[i]:
        count += 1
        i += 1

    i = suffix_array_id - 1
    while pattern_length <= lcp[i]:
        i -= 1
        count += 1

    return count

def main():
    txt = open('data/text.txt', encoding='utf-8')
    text = txt.read()
    text += "$"
    suffix_array = create_suffix_array(text)
    inversed_suffix_array = create_inverse_suffix_array(len(text), suffix_array)
    lcp = create_lcp(text, suffix_array, inversed_suffix_array)
    lcp_left_right = precompute_binary_lcp(lcp)
    print(suffix_array)

    while True:
        pattern = input()
        #search the pattern
        suffix_array_id = binary_search(text, suffix_array, pattern, lcp_left_right)
        count = count_results(suffix_array_id, len(pattern), lcp)
        if suffix_array_id:
            print("Вхождение строки найдено на {} позиции".format(suffix_array_id))
            print("Всего вхождений: {}".format(count))
        else:
            print("Вхождение строки не найдено!")

if __name__ == "__main__":
    main()
