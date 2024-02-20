pprice = float(input("Enter purchase price : "))
sprice = float(input("Enter sell price : "))
print("percentage : ", round(((sprice-pprice)/sprice) * 100,0),"%")