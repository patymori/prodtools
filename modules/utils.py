# code = utf-8


def how_similar(this, that):
    import difflib
    if this is None:
        this = ''
    if that is None:
        that = ''
    return difflib.SequenceMatcher(None, this.lower(), that.lower()).ratio()


def similarity(items, text):
    r = {}
    for item in items:
        rate = how_similar(item, text)
        if not rate in r.keys():
            r[rate] = []
        r[rate].append(item)
    return r


def ranking(similarity, expected_ratio=0):
    r = []
    ratio_list = similarity.keys()
    ratio_list.reverse()
    for ratio in ratio_list:
        if ratio > expected_ratio:
            for item in similarity[ratio]:
                r.append(item)
    print(r)
    return r