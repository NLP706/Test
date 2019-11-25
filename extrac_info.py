# 施工合同纠纷  基本标签的提取
import re
#docu_name = "（2015）江宁民初字第5033号"
#docu_name1 = "（2018）苏05民终3176号"
#docu_name2 = "（2015）吴江开民初字第01988号"
#docu_name3 = "（2014）石民六终字第01468号"
#docu_name4 = "（2017）苏0324民初4828号"
def parse_content(docu_name):
    type_ = ['民', '刑']
    content_dict = {}
    year = docu_name.split('）')[0].replace('（', '')
    content_dict['年份'] = year
    content = docu_name.split('）')[1]
    for t in type_:
        if t in content:
            content_dict['案件类型'] = t
            content = content.split(t)
            content_dict['地域简称'] = content[0]
            if '字' in content[1]:
                # content[1]:初字第XXX号
                content = content[1].split('字')
                content_dict['审判阶段'] = content[0]
                #content[1] :第XXX号,提取数字
                content_dict['案件序号'] = re.findall(r'\d+',content[1])[0]
            else:
                #content[1]: 初xxx号
                content_dict['案件序号'] = re.findall(r'\d+', content[1])[0]
                content_other = re.findall(r'\D', content[1])
                content_dict['审判阶段'] = content_other[0]
    s = []
    for k in content_dict.keys():
        s.append(k + '：' +  content_dict[k])
        #print(k)
    return '||'.join(s)
#co_dict = parse_content(docu_name4)
#print(co_dict)
def parse_document_name(do: list, t: str):
    try:
        return [i for i in do if i in t][0]
            
    except Exception:
        return ''

import os
import json
do_type = ['判决书','裁定书','调解书','决定书','通知书','令','检察院终结性文书']
do_stage = ['一审','二审','再审','再审审监','复核','非诉执行','刑罚变更']
id_list = ['委托诉讼代理人\诉讼代表人', '被上诉人（原审第三人）', '委托诉讼代理人', '委托代理人', '法定代表人', '法定代理人', 
'原审第三人', '被上诉人', '负责人', '第三人', '代表人', '投资人', '经营者', '原告', '被告']

r5 = re.compile('原告|被告|负责人|委托代理人|委托诉讼代理人|法定代表人|委托诉讼代理人\诉讼代表人|第三人|法定代理人|代表人|投资人|被上诉人|被上诉人（原审第三人）|原审第三人|经营者', re.U)

filePath = r'D:\nlp706\施工合同纠纷\1000file\中交一航局第四工程有限公司与曹妃甸港集团股份有限公司建设工程施工合同纠纷一审民事判决书.json'


w_data = open(r'D:\nlp706\施工合同纠纷\corpus_data.txt','w',encoding = 'utf-8')

for root, dirs, files in os.walk(r'D:\nlp706\施工合同纠纷\1000file'):
    for name in files:
        w = []
        filePath = os.path.join(root, name)
        fname, ext = os.path.splitext(name)
        if '-' in filePath:
            print(fname)
        else:

            filejson = json.load(open(filePath, "rb"))
            # 文书名称
            t1 = filejson['data'].get('TITLE', name)
                # 文书类型
            t1_1 = parse_document_name(do_type, t1)
                # 案件阶段
            t1_2 = [filejson['data']['lsws'][0]['SPCX'] if len(filejson['data']['lsws']) != 0 else parse_document_name(do_stage, t1)][0]
            
            w.append('文书名称：' + t1)
            w.append('文书类型：' + t1_1)
            w.append('案件阶段：' + t1_2)
            
            # 判决机关与文书编号
            if len(filejson['data']['baseList']) == 3:                
                w.append('判决机关：' + filejson['data']['baseList'][0])
                w.append('文书编号：' + filejson['data']['baseList'][1])
                if filejson['data']['baseList'][1]:
                    w.append(parse_content(filejson['data']['baseList'][1]))
                
            else: 
                w.append('判决机关：' + filejson['data']['JBFY'])
                w.append('文书编号：' + filejson['data']['WSAH'])
                if filejson['data']['WSAH']:
                    w.append(parse_content(filejson['data']['WSAH']))
            
            # 控辩双方人员基本情况类
            t3 = filejson['data']['contents'][0]['content']
            if len(t3) != 0:
                t33 = []
                for t in t3:
                    t = t.replace('。', '')                  
                    if '：' in t:
                        t = re.split('[，|：]', t)
                        t33.append(t[0] +'：' + t[1] + '||' + '||'.join(t[2:]))
#                        print(t33)
#                        t33.extend(t)

                    elif r5.search(t):
                        for idl in id_list:
                            if idl in t:
                                t = t.replace(idl, idl + '，')
                                break                           
                        t = t.split('，')
                        t33.append(t[0] +'：' + t[1] + '||' + '||'.join(t[2:]))
#                        print(t33)
#                        t33.extend(t)
                    
                    else:
                        pass
#                        print(t)
#                print(t33)
            w.append(''.join(t33))
#            print(w)
        w_data.write('||'.join(w)+'\n')

w_data.close()