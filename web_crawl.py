#!/usr/bin/env python3

import re
import favicon
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import csv,os

#Function to find all nested URL's within the given link.
def find_urls(link):
    url=[]
    for a in soup.find_all('a', href=True):
        if (a['href'] not in url and len(a['href'])>1):
            url.append(a['href'])
    if (len(url)>=1):
        url=[link+i if i[0]!="h" else i for i in url]
        url.insert(0,link)
        return url
    return None

#Function to find a pattern within a URL using regex.
def find_pattern(url,pattern=".*"):
    r=re.compile(pattern)
    res=list(filter(r.findall,url))
    if res is None:
        return None
    return res


def college_name(link):
    title=soup.title
    title=title.string
    if("Home" in title):
        name=re.search(r"([|])([a-zA-Z. &]*)",title)
        try:
            return name[2].strip()
        except:
            return None
    else:
        name=re.search(r"([a-zA-Z. &]*)",title)
        return name[0]


def find_phone(urls):
    #Searching homepage
    text=soup.get_text()
    ph=re.search(r"(\d{10})|([\+]{0,1}\d{10,13}|[\(][\+]{0,1}\d{2,}[\13)]*\d{5,13}|\d{2,6}[\-]{1}\d{2,13}[\-]*\d{3,13})",text)
    if ph is not None:
        return ph[0]
    #Searching nested URL's
    else:
        res=find_pattern(urls,"contact|Contact")
        for url in res:
            req=Request(url)
            html=urlopen(req).read()
            s=BeautifulSoup(html,'html.parser')
            text=s.get_text()
            ph=re.search(r"([\+]{0,1}\d{10,13}|[\(][\+]{0,1}\d{2,}[\13)]*\d{5,13}|\d{2,6}[\-]{1}\d{2,13}[\-]*\d{3,13})",text)
        if ph is not None:
            return ph[0]
        else:
            return None


def find_youtube(urls):
    res=find_pattern(urls,"youtube")
    if len(res)>0:
        return res[0]
    return None


def find_logo(link):
    icons=favicon.get(link)
    try:
        icon=icons[0]
    except:
        return None
    try:
        icon=icons[1]
    except:
        pass

    res=requests.get(icon.url,stream=True)
    #Saves logo of the form college_name.format in the working directory.
    with open("{}.{}".format(name,icon.format),"wb") as image:
        for chunk in res.iter_content(1024):
            image.write(chunk)
    if name is not None:
        fname=name+icon.format
        return  fname
    else:
        return None


def email(urls):
    #Searching homepage
    text=soup.get_text()
    mail=re.search(r"\w+\@[\w+\.\w+]*",text)
    if mail is not None:
        return mail[0]
    #Searching nested URL's
    else:
        res=find_pattern(urls,"contact|Contact|about")
        for url in res:
            req=Request(url)
            html=urlopen(req).read()
            s=BeautifulSoup(html,'html.parser')
            text=s.get_text()
            mail=re.search(r"\w+\@[\w+\.\w+]*",text)
        if mail is not None:
            return mail[0]
        else:
            return None


def find_address(urls):
    para=[]
    #Searching homepage
    for p in soup.find_all("p",{"class":"rtin-des"}):
        if (p not in para):
            para.append(p)
    #Searching nested URLS's
    res=find_pattern(urls,"contact|Contact|About|about")
    for url in res:
        req=Request(url)
        try:
            html=urlopen(req).read()
        except:
            continue
        s=BeautifulSoup(html,'html.parser')
        for p in soup.find_all(["p","a"],{"class":"rtin-des","class":"text-gray"}):
            if (p not in para):
                para.append(p)
    text=[]
    #Extracting only text from HTML p tags
    for tag in para:
        sp=BeautifulSoup(str(tag),"html.parser")
        text.append(sp.get_text())
    text.sort(key=len)
    #Returning text with largest length
    if len(text)>0:
        adr=text[len(text)-1]
        adr=re.sub(" +"," ",adr)
        return adr.replace("\r\n","\n").strip()
    else:
        return None


def pincode(urls):
    #Searching homepage
    if adr is not None:
        pin=re.search("([0-9]{6}|[0-9]{3}\s[0-9]{3})",adr)
        return pin[0]
    text=soup.get_text()
    pin=re.search(r"^[1-9][0-9]{5}$",text)
    if pin is not None:
        return pin[0]
    #Searching nested URLS's
    else:
        res=find_pattern(urls,"contact|Contact")
        for url in res:
            req=Request(url)
            html=urlopen(req).read()
            s=BeautifulSoup(html,'html.parser')
            text=s.get_text()
            pin=re.search(r"^[1-9][0-9]{5}$",text)
        if pin is not None:
            return pin[0]
        else:
            return None


def find_about(urls):
    para=[]
    #Searching Homepage
    for p in soup.find_all("p",string=re.compile(rf"College|{name}")):
        if (p not in para):
            para.append(p)
    #Searching nested URL's
    res=find_pattern(urls,"contact|Contact|About|about")
    for url in res:
        req=Request(url)
        html=urlopen(req).read()
        s=BeautifulSoup(html,'html.parser')
        for p in soup.find_all("p",string=re.compile(rf"College|{name}")):
            if (p not in para):
                para.append(p)
    text=[]
    #Extracting text from HTML tags
    for tag in para:
        sp=BeautifulSoup(str(tag),"html.parser")
        text.append(sp.get_text())
    text.sort(key=len)
    #Returning largest length text
    if len(text)>0:
        return text[len(text)-1]
    else:
        return None

#Function to create CSV file
def report(rows):
    keys=["College Name","Website","Youtube Link","Logo","Phone","email","Address","Pincode","About"]
    with open("report.csv","a+") as fh:
        w=csv.writer(fh)
        if fh.tell()==0:
            w.writerow(keys)
        w.writerow(rows)


if __name__=="__main__":
    clg_urls=["https://www.sjcem.edu.in","https://www.sfit.ac.in/"]
    count=1
    for link in clg_urls:

        req=Request(link)
        html=urlopen(req).read()
        soup=BeautifulSoup(html,'html.parser')

        global urls
        urls=find_urls(link)

        name=None
        web=None
        yt=None
        logo=None
        ph=None
        mail=None
        adr=None
        pin=None
        about=None


        details=[]

        if(name is None):
            name=college_name(link)

        details.append(name)

        if(web is None):
            web=link
        details.append(web)

        if(yt is None):
            yt=find_youtube(urls)
        details.append(yt)

        logo_name=find_logo(link)
        details.append(logo_name)

        if(ph is None):
            ph=find_phone(urls)
        details.append(ph)

        if(mail is None):
            mail=email(urls)
        details.append(mail)

        if adr is None:
            adr=find_address(urls)
        details.append(adr)

        if(pin is None):
            pin=pincode(urls)
        details.append(pin)

        if(about is None):
            about=find_about(urls)
        details.append(about)

        report(details)

        print("Details of College {} were added successfully.".format(count))
        count+=1
