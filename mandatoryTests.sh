for f in $(find ./mandatoryTest -type f) ; do
    echo -e "\n$f"
    sed "/)/q" $f
    python3 Compiler.py $f out.mr && maszyna_wirtualna/maszyna-wirtualna out.mr
    echo
    read -p "Press key to continue.. " -n1 -s
    echo
done