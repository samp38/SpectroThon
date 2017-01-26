#!/usr/bin/sh

ssh root@192.168.0.10 '
    cd /usr/share/matrix-gui-2.0
    rm patterns/*.csv
    rm patterns/*.bmp
    rm patterns/*.sdf
    rm tmp/*
    rm *.bmp
    dlp_nirscan -A9 -Z1684 -N85
    if [ $? -eq 255 ];
        then
        echo "failed" > tmp/script_status499.txt
        exit 0
    fi
    cd patterns/
    dlp_nirscan -Pscan.sdf
    if [ $? -eq 255 ];
        then
        echo "failed" > ../tmp/script_status499.txt
        exit 0
    fi
    count=0
    for entry in *; do
        case $entry in *.bmp)
            convert $entry -virtual-pixel Black  -filter point -interpolate nearestneighbor -distort polynomial "2 $(cat /usr/share/matrix-gui-2.0/calibration_data/control_points.txt)" scan_img.bmp
            mv scan_img.bmp $entry
            count=$((count+1));;
        esac
    done
    dlp_nirscan -l$count
    cd ..
    dlp_nirscan -S85 -E1400 -fcustom_scan
'
