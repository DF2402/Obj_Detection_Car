import csv

data = [
    {'index': '1', 'area': '10000', 'cx': 400, 'ctrl': 'right'},
    {'index': '2', 'area': '160000', 'cx': 100, 'ctrl': 'right'},
    {'index': '3', 'area': '90000', 'cx': -400, 'ctrl': 'left'},
    {'index': '4', 'area': '10000', 'cx': 0, 'ctrl': 'forward'}
]

try:
    with open('./23Mar/test_case.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'area', 'cx', 'ctrl']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()  # Write header
        writer.writerows(data)  # Write data rows

    print("CSV file created successfully at: test_case.csv")

except Exception as e:
    print(f"Error: {e}")
    print("Check file permissions, path, or data formatting.")