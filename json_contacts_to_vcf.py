# -*- coding: utf-8 -*-
#python 3.x

import sys
import re
import json
#USAGE:
#json_contacts_to_vcf.py path_to/contacts.json

def get_contacts_from_json(path='result.json')->list:    
    with open(path, 'r',encoding='utf-8') as file:
        _base_list = json.load(file)['contacts']['list']
        
    fields=('last_name', 'first_name', 'phone_number') # формируем рабочий список без лишних записей и ключей
    _ld=[]
    for k in _base_list:
        if set(fields).issubset(k.keys()):             #фильтр по наличию необходимых ключей
            _ld.append( {'first_name': k['first_name'],
                        'last_name': k['last_name'],
                        'id': (k['first_name']+' '+k['last_name']).strip(),
                        'phone_number':  re.sub(r'^00', '+', ''.join(re.findall(r'(^\+|\d)', k['phone_number'] ))   ),
                         #'email': k['email']
                       } )
            
    print(f'json have {len(_base_list)}  notes, was chosen  {len(_ld)} contacts')
    return _ld
    
def compare(_lt)->str:
    t=list(filter(None, _lt))
    if not t:
        return ''
    else:
        return min(t)
        
def merging_duplicates(_ld)->list: #объединяет схожие записи по имени или номеру
    _phone_d={} 
    _name_d={} 
    _merged=[]
    
    for k in _ld: #при совпадении номеров, выбираем КОРОТКИЕ имена
        if k['phone_number'] in _phone_d:
            _merged.extend([ _phone_d[k['phone_number']]['id']+k['phone_number'],  k['id']+k['phone_number'] ])
            
            _phone_d[k['phone_number']]['last_name']=compare( _phone_d[k['phone_number']]['last_name'], k['last_name'])
            _phone_d[k['phone_number']]['first_name']=compare( _phone_d[k['phone_number']]['first_name'], k['first_name'])        
        else:
            _phone_d[k['phone_number']]=k

    for k in _phone_d.values():   #при совпадении имен, собираем номера
        if k['id'] in _name_d:
            _merged.extend([ k['id']+_name_d[k['id']]['phone_number'],  k['id']+k['phone_number'] ])
            _name_d[k['id']]['phone_number']+=f';{k["phone_number"]}'  
            #print(_name_d[k['id']] , k)
        else:
            _name_d[k['id']]=k

    print('merged : ' + str(len(set(_merged))) )
    print('\n',*_merged, sep='\n')  #optional
    return(_name_d.values())
    


def write_vcf(rows, path=''):
    with open(path+'_ALL.vcf', 'w',encoding='utf-8') as allvcf:
        i = 0
        for row in rows:
            st='BEGIN:VCARD\n'
            st+='VERSION:3.0\n'
            st+=f'''N:{row['last_name']};{row['first_name']};;;\n'''
            st+=f'''FN:{row['id']}\n'''
            st+="\n".join([f'TEL;TYPE=CELL:{k}' for k in row['phone_number'].split(';') ])+"\n" #по одному номеру на строку
            #st+=f'EMAIL:{row[3]}\n'
            st+='END:VCARD\n'
            
            allvcf.write(st)
            i += 1#counts
            
    print ('\n',str(i) + " vcf cards generated")

def main(args):
    if len(args)==2:
        path =args[1]
    elif type(args) is str:
        path =args
    else:
        path = 'result.json'
        
    rows=get_contacts_from_json(path)
    rows=merging_duplicates(rows) #optional
    write_vcf(rows, path)

if __name__ == '__main__':
   main(sys.argv)
