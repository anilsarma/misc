#git clone git@github.com:anilsarma/misc.git
cd misc/njt
git pull

before=`git log  --pretty='%H' master|head -1`
python check_for_changes.py
after=`git log  --pretty='%H' master|head -1`

EMAIL=<>
# send out and email if the version file has been updated.
if [ "$before" != "$after" ]; then 
  python ../google/gmail/gmail_send.py --to "$EMAIL" --from "$EMAIL" --subject "updated NJ Transit" --body ./version.txt;
fi
cat ./version.txt

