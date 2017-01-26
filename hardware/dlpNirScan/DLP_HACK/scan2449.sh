rm patterns/*.csv
rm patterns/*.bmp
rm patterns/*.sdf
rm tmp/*
rm *.bmp
echo "Generating Patterns..." > tmp/script_status876.txt
dlp_nirscan -A9 -Z1683 -N85
if [ $? -eq 255 ];
 then
 echo "failed" > tmp/script_status876.txt
 exit 0
 fi
cd patterns/
echo "Preparing Scan Solution..." > ../tmp/script_status876.txt
dlp_nirscan -Pscan.sdf
if [ $? -eq 255 ];
 then
 echo "failed" > ../tmp/script_status876.txt
 exit 0
 fi
echo "Loading Patterns..." > ../tmp/script_status876.txt
count=0
for entry in *
do
case $entry in *.bmp)
convert $entry -virtual-pixel Black  -filter point -interpolate nearestneighbor -distort polynomial "2 $(cat /usr/share/matrix-gui-2.0/calibration_data/control_points.txt)" scan_img.bmp
mv scan_img.bmp $entry
count=$((count+1));;
esac
done
dlp_nirscan -l$count

cd .. 
dlp_nirscan -S85 -E1400 -fcustom_scan
#Using a more unique string to detect if the script is completed
echo "_?!!SCRIPT_COMPLETED!!?_" > tmp/script_status876.txt