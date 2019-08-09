# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 23:52:34 2019

@author: Abhis
"""

#############################
#product matching to thesis
import re
import pandas as pd
import mysql.connector
from product_cleaner import product_dict_cleaner
import sys
def product_start_index():
    con=pymysql.connect(host='127.0.0.1',  # your host name is often 'localhost'
                     user='root',            
                     passwd='profeza@123',  
                     db='smart_sales_app',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)
    with con:
        cur=con.cursor()
        cur.execute("SELECT thesis_id FROM thesis ORDER BY thesis_id DESC LIMIT 1;")
        last_id = cur.fetchone()["thesis_id"]
    product_query = ("SELECT product_id FROM product WHERE thesis_done_id < %s ORDER BY product_id ASC LIMIT 1")
    with con:
        cur=con.cursor()
        cur.execute(product_query,(last_id,))
        rows=cur.fetchone()
        product_index_start = rows["product_id"]
        if len(rows) == 0:
            return -1, 0 
        return product_index_start,last_id
        
        
            
# =============================================================================
# 1.obtain keywords for that product id and map keyword id to the thesis        
# PRODUCTBATCH
# THESIS BATCH TILL COMPLETETED 
# THEN AGAIN REPEATED
# =============================================================================

# =============================================================================
# 
# SELECT product_id FROM product WHERE thesis_id<=453 ORDER BY product_id ASC LIMIT 1 ;
# =============================================================================
import pymysql.cursors
def batch_index(query,batch_size=100,index=0):
    control = True
    #index = 0
    query1 = query + " LIMIT "+str(batch_size)+" OFFSET "+str(1*index)
    while control==True:
       con=pymysql.connect(host='127.0.0.1',  # your host name is often 'localhost'
                     user='root',            
                     passwd='profeza@123',  
                     db='smart_sales_app',
                     charset='utf8mb4',
                     cursorclass=pymysql.cursors.DictCursor,
                     autocommit=True)
       with con:
            print("aggain")
            cur = con.cursor()
            cur.execute(query1)
            rows = cur.fetchall()
            if len(rows)== 0:
                control=False
            index1 = index + batch_size
       return rows, index1, control
# =============================================================================
# 
def matching_over_thesis_insert(id_pro_c,thesis_dict,brand_id, category_id,insert):
    for key, value in id_pro_c.items():
        for key1, value1 in thesis_dict.items():
            if len(value)==1:
                for item in value:
                    reg="\s"+item+"\s"
                    if re.search(reg,value1, re.I):
                        insert(key,brand_id[key], category_id[key],key1)
            elif len(value) > 1:
                grep={}
                print("more than two keywords")
                for item in value:
                    reg="\s?\S+\s?\S+\s?\S+\s?\S+\s?"+item+"\s\S+\s?\S+\s?\S+\s?\S+\s?\S+"
                    try: match = re.findall(reg,value,re.I)
                    except: continue
                    grep[item] = match
                for k, v in grep.items():
                    for item in value:
                        if item!=key:
                            reg="\s"+item+"\s"
                            if re.search(reg,v.re.I):
                                print("match found",key)
                                insert(key,brand_id[key], category_id[key],key1)
                                
                                

def insert(pro_id,bran_id,cat_id,the_id):
    con=pymysql.connect(host='127.0.0.1',  # your host name is often 'localhost'
                         user='root',            
                         passwd='profeza@123',  
                         db='smart_sales_app')
    query="INSERT INTO product_has_thesis (product_product_id,product_brand_brand_id,product_category_category_id,thesis_thesis_id) VALUES (%s,%s,%s,%s)"
    cursor = con.cursor()
    try:
        cursor.execute(query,(pro_id,bran_id,cat_id,the_id,))
        con.commit()
    except Exception as e:
        print(e)
        print("not insert")
    finally:
        cursor.close()
        con.close
        
def update_thesis_done_id(last_id, product_id_list):
    con=pymysql.connect(host='127.0.0.1',  # your host name is often 'localhost'
                         user='root',            
                         passwd='profeza@123',  
                         db='smart_sales_app')
    query="UPDATE `smart_sales_app`.`product` SET `thesis_done_id` = %s WHERE `product_id` = %s"
    cursor = con.cursor()
    try:
        for product_id in product_id_list:
            cursor.execute(query,(last_id, product_id,))
            con.commit()
    except Exception as e:
        print(e)
        print("not update")
    finally:
        cursor.close()
        con.close
    
                        
    
# =============================================================================


################################################
#code
pro_start_index, last_id = product_start_index()
if pro_start_index==-1:
    sys.exit(0)
#####include result -1 
control=True
rindex = pro_start_index-1
while control == True:
    rows, rindex, control = batch_index(query="Select product_id, product_name, brand_brand_id, category_category_id, thesis_done_id from product", index=rindex)
    id_pro_c={}
    thesis_pro_id={}
    thesis_id=[]
    brand_id={}
    category_id={}
    for row in rows:
        thesis_id.append(row["thesis_done_id"])
        id_pro_c[row['product_id']] = row['product_name']
        brand_id[row['product_id']] = row['brand_brand_id']
        category_id[row['product_id']] = row['category_category_id']
        if not row["thesis_done_id"] in thesis_pro_id.keys():
            thesis_pro_id[row["thesis_done_id"]] = [row["product_id"]]
        thesis_pro_id[row["thesis_done_id"]].append(row["product_id"])
    id_pro_c = product_dict_cleaner(id_pro_c)
    if len(thesis_pro_id.keys())==1:
        print("first 1")
        tindex=thesis_id[0]
        tcontrol=True
        while tcontrol == True:
            thesis_dict, tindex, tcontrol = batch_index(query="SELECT thesis_id, thesis_keywords from thesis",index=tindex)
            thesis_id_keywords={}
            for row in thesis_dict:
                thesis_id_keywords[row["thesis_id"]] = row["thesis_keywords"]
            matching_over_thesis_insert(id_pro_c,thesis_id_keywords,brand_id, category_id,insert)
        product_id_list = [i for i in id_pro_c.keys()]
	    update_thesis_done_id(last_id, product_id_list)
	    print("first end")
            
            print("first end")
    elif len(thesis_pro_id.keys())>1:
        print("many 1")
        for ke, val in thesis_pro_id.items():
            #product_keyword=[id_pro_c[n] for n in val]
            id_pro_c1={}
            for num in val:
                id_pro_c1[num] = id_pro_c[num]
            
            tindex=ke
            tcontrol=True
            while tcontrol == True:
                thesis_dict, tindex, tcontrol = batch_index(query="SELECT thesis_id, thesis_keywords from thesis",index=tindex)
                thesis_id_keywords={}
                for row in thesis_dict:
                    thesis_id_keywords[row["thesis_id"]] = row["thesis_keywords"]
                matching_over_thesis_insert(id_pro_c1,thesis_id_keywords,brand_id, category_id,insert)
                print("finally innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
		    product_id_list = [i for i in id_pro_c1.keys()]
		    update_thesis_done_id(last_id, product_id_list)
		    print("many end")
	                

##############################
#First, get the last thesis_id, and get the product which are not run over some thesis
#