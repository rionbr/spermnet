#<key id="d11" for="node" attr.name="core" attr.type="boolean"/>
#<key id="d9" for="node" attr.name="module-svd-DM-1" attr.type="boolean"/>
#<key id="d21" for="node" attr.name="module-svd-DM-2" attr.type="boolean"/>
#<key id="d17" for="node" attr.name="module-svd-DM-3" attr.type="boolean"/>
#<key id="d20" for="node" attr.name="module-svd-DM-5" attr.type="boolean"/>
#<key id="d10" for="node" attr.name="module-svd-DM-7" attr.type="boolean"/>
#<key id="d26" for="node" attr.name="module-svd-DM-8" attr.type="boolean"/>
#<key id="d18" for="node" attr.name="module-svd-DM-9" attr.type="boolean"/>
#<key id="d28" for="node" attr.name="module-svd-DM-10" attr.type="boolean"/>
#<key id="d19" for="node" attr.name="module-svd-DM-11" attr.type="boolean"/>


# Define paths
gp="/home/casci/rionbr/spermnet/4-network/results/graphml"
cp="/home/casci/rionbr/spermnet/4-network/results/forceatlas2"
op="/home/casci/rionbr/spermnet/4-network/images/graphs"

# celltype
celltype="spermatocyte"
# Network
network="thr"
# Threshold
threshold="0p5"
# Layer
layer="DM"
# Rotation
rotate=290


echo "-- Plotting $celltype-$network-$threshold-$layer-multi-mod --"
#
highlight="${pairs[$module]}"
#
input="$gp/$celltype/net-$celltype-$network-$threshold-$layer.graphml"
coords="$cp/$celltype/net-$celltype-$network-$threshold-$layer-forceatlas2.txt"
#
pdfpath="$op/$celltype/$layer/pdf"
jpgpath="$op/$celltype/$layer/jpg"
#
pdf="$pdfpath/net-$celltype-$network-$threshold-$layer-mod-multi.pdf"
jpg="$jpgpath/net-$celltype-$network-$threshold-$layer-mod-multi.jpg"

mkdir -p $pdfpath
mkdir -p $jpgpath

# Build
echo "-- Build Main.java --"
javac -cp gephi-toolkit-0.9.2-all.jar PlotNetMultiModDM.java

# Run GephiLoadAndPlot
java -cp gephi-toolkit-0.9.2-all.jar:. PlotNetMultiModDM --input $input --coords $coords --output $pdf --rotate $rotate

# Convert PDF to JPG
convert -density 300 -resize 3300x2550 $pdf $jpg