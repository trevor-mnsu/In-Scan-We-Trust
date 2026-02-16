'''
Look for dosage information in the text.
Often labeled as "dosage:" or "dosage instructions"
May be seperated into boxes or multiple lines 
This can lead to seperation of information. We need to avoid this. 

1) Search for "dosage:" try and find the information
2) Search for dosage box
3) Try and seperate split up information into multiple lines (Page Segmentation, Order Detection)
'''