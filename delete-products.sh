# WARNING: this will silently delete both of your indexes
echo "Deleting Products"
curl -k -X DELETE -u admin  "https://localhost:9200/bbuy_products"
if [ $? -ne 0 ] ; then
  echo "Failed to delete products index"
  exit 2
fi
