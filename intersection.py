
ma_fans = "data/active_uniq_ids-m19-2th.txt"
eng_fans = "data/active_uniq_ids-tsaieng.txt"


with open(ma_fans) as fp:
    ma_fans_list = fp.readlines()
    ma_fans_list = map(lambda x:x.strip(), ma_fans_list)

with open(eng_fans) as fp:
    eng_fans_list = fp.readlines()
    eng_fans_list = map(lambda x:x.strip(), eng_fans_list)


ma_fans_set = set(ma_fans_list)
eng_fans_set = set(eng_fans_list)


print len(ma_fans_set.intersection(eng_fans_set))



