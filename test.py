import pandas as pd

df=pd.read_csv("cleaned_zomato.csv")


print(df["votes"].unique())

print(df["approx_cost"].unique().sort)