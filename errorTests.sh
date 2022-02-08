for f in $(find ./errorTest -type f -name "error*.imp") ; do
    echo -e "\n$f"
    sed "/)/q" $f
    python3 Compiler.py $f out.mr
    echo
    read -p "Press key to continue.. " -n1 -s
    echo
done