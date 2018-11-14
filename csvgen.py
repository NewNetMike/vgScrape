from funcs import *
import csv

data = load_data("data.json")
headers = "*Action(SiteID=US|Country=US|Currency=USD|Version=941),*ProductName,SaleTemplateName,*Category,Product:UPC,Product:ISBN,Product:EAN,Product:EPID,Product:Brand,Product:MPN,Product:IncludePreFilledItemInformation,Product:IncludeStockPhotoURL,Product:ReturnSearchResultsOnDuplicates,Title,Subtitle,Description,*ConditionID,PicURL,*Quantity,*Format,*StartPrice,BuyItNowPrice,*Duration,ImmediatePayRequired,*Location,GalleryType,PayPalAccepted,PayPalEmailAddress,PaymentInstructions,StoreCategory,ShippingDiscountProfileID,DomesticRateTable,ShippingType,ShippingService-1:Option,ShippingService-1:Cost,ShippingService-1:Priority,ShippingService-1:ShippingSurcharge,ShippingService-2:Option,ShippingService-2:Cost,ShippingService-2:Priority,ShippingService-2:ShippingSurcharge,DispatchTimeMax,CustomLabel,ReturnsAcceptedOption,RefundOption,ReturnsWithinOption,ShippingCostPaidByOption,AdditionalDetails,ShippingProfileName,ReturnProfileName,PaymentProfileName,ConditionDescription".split(",")

print(headers)

rows = list()

for key in data.keys():
    item = data[key]
    rec_sell = item["suggested_sell_price"]
    if rec_sell != "N/A":
        #print(rec_sell)
        title = item["product_name"]
        upc = item["upc"].split(",")[0]
        epid = item["epid"]
        image = item["image"]
        price = float(item["suggested_sell_price"])
        rows.append("Add,{},,139973,{},,,{},,,,,,{},,Disc or cartridge only in good condition. May have scratches or other cosmetic wear that does not affect gameplay.<br>Depending on what we have in stock may also include case and/or manual. Contact us for item-specific information.,6000,{},1,FixedPrice,{},,GTC,1,97008,,1,mycxle@gmail.com,,,,,Flat,USPSFirstClass,0,,,,,,,3,,ReturnsNotAccepted,,,,,,,,Disc or cartridge only in good condition. May have scratches or other cosmetic wear that does not affect gameplay. Depending on what we have in stock may also include case and/or manual. Contact us for item-specific information.".format(title, upc, epid, title, image, price))


with open('upload.csv', 'w', newline="") as outcsv:
    writer = csv.writer(outcsv)
    writer.writerow(headers)
    for r in rows:
        print(r)
        writer.writerow(r.split(","))



print(data)