# scRNA-seq pipeline

## Features

> - from fastq to expression matrix
> - 用于预处理3'端scRNA-seq



## Intro to protocols

- [smart-seq2](<https://www.illumina.com/science/sequencing-method-explorer/kits-and-arrays/smart-seq2.- html>)

![img](https://www.illumina.com/content/dam/illumina-marketing/images/tools/sequencing/smart-seq2.png)

smart-seq2最大的特色是添加了链反转引物(Template Switching Oligo, TSO) CCC，这样就可以合成全长RNA。缺点是必须一个细胞建一个库，无法进行early multiplexing。后来为了增加建库效率，有文章[^1]在oligo(dT) primer上添加barcode和UMI，以实现early multiplexing。这里给一个例子：

> TCAGACGTGTGCTCTTCCGATCT-**AACGTGAT**-NNNNNNNN-ttttttttttttttttttttttttt
>
> 5‘- cDNA forward adapter + barcode + UMI + 25nt oligo dT

这里我的pipeline针对的是modified (early multiplexing) smart-seq2

- `10X Chromium`

![](https://img1.dxycdn.com/2018/0809/241/3293783459839233958-8w.png)

V2和V3的区别：

|-- 5'- cDNA forward adapter + 16-bp cell barcode + 10-bp UMI + (T)30 - 3'  **V2** (16+10)

|-- 5'- cDNA forward adapter + 16-bp cell barcode + 12-bp UMI + (T)30 - 3'  **V3 **(16+12)

更多细节看[这里](<https://teichlab.github.io/scg_lib_structs/methods_html/10xChromium3.html>)

[^1]:<https://www.cell.com/cell-stem-cell/fulltext/S1934-5909(17)30078-4#secsectitle0075>



---

## 下机数据

### modified smart-seq2

![](https://raw.githubusercontent.com/JarningGau/blog_images/master/20190821/scRNA-seq-pipeline-01.png)

barcode和UMI的信息都可以从R2中提取出来。

### 10X (V2)

这里给一个示例：

```shell
├── [237M] neurons_900_S1_L001_I1_001.fastq.gz
├── [642M] neurons_900_S1_L001_R1_001.fastq.gz
├── [1.8G] neurons_900_S1_L001_R2_001.fastq.gz
├── [238M] neurons_900_S1_L002_I1_001.fastq.gz
├── [646M] neurons_900_S1_L002_R1_001.fastq.gz
└── [1.8G] neurons_900_S1_L002_R2_001.fastq.gz
```

`R1` 26-bp  (16+10)

`R2` 98-bp (transcript)

`I1` 8-bp (I7 sample barcode)

大部分作者在上传数据时，一般没有`I1`。

---

> 一般10X的数据用`10X genomics`公司`cell ranger`软件就行了，但是有时候我们需要一些更加个性化的分析（比如分析转录组中的转座子活性），这时候就需要能够有一个高度定制化的流程。

## 处理流程

主要的流程参考：[单细胞文档](<https://umi-tools.readthedocs.io/en/latest/Single_cell_tutorial.html>)

### 需要的软件：

- [umi-tools](<https://umi-tools.readthedocs.io/en/latest/>)
- flexbar (for reads trimming)
- STAR    [manual](<http://labshare.cshl.edu/shares/gingeraslab/www-data/dobin/STAR/STAR.posix/doc/STARmanual.pdf>)
- featureCounts
- samtools
- [TEToolkit](<http://hammelllab.labsites.cshl.edu/software/>)：用来分析转座子活性；[github](<https://github.com/mhammell-laboratory/tetoolkit>)

### 需要的参考文件：

- `barcodes`，直接提供(modified smart-seq2)或由umi_tools直接生成(10X)，需要注意的是，直接生成需要知道细胞的数量。所以在处理公共数据的时候，最好使用作者提供的barcodes序列。如果实在不知道，可以使用`umi_tools whitelist`命令估计细胞数量。
- Reads trimming related：
  - `adapters_polyA.fa`：根据个人需要定制
  - `TSO.fa`：modified smart-seq2特有的
- 转录组注释文件：
  - `genes.gtf`，：一般从[gencode](<https://www.gencodegenes.org/>)直接下载
  - `TE.gtf`：[这里](<http://labshare.cshl.edu/shares/mhammelllab/www-data/TEToolkit/TE_GTF/>)有整理好的。(TEToolkit)

- STAR索引

```shell
# build genes index
STAR --runThreadN 24 --runMode genomeGenerate \
--genomeDir STARIndexERCC/gencode.vM21 \
--genomeFastaFiles WholeGenomeFasta/genome_with_ERCC.fa \
--sjdbGTFfile Annotation/gencode.vM21.withERCC92.gtf \
--sjdbOverhang 100
# 参数很简单，只解释最后一个
# --sjdbOverhang specifies the length of the genomic sequence around the 
# annotated junction to be used in constructing the splice junctions database
```

### 下面是具体的代码：

以一个modified smart-seq2的文库`E8M(96 cells)`为例

```shell
# step1: (optional) Identify correc cell barcodes (skip)

# step2: Extract barcodes and UMIs and add to read names (single-core)
time umi_tools extract \
--bc-pattern CCCCCCCCNNNNNNNN \
--stdin E8M_R2.clean.fq.gz \
--stdout E8M_R2_extracted.clean.fq.gz \
--read2-in E8M_R1.clean.fq.gz \
--read2-out E8M_R1_extracted.clean.fq.gz \
--filter-cell-barcode \
--whitelist barcodes.txt

# step3: (optional) Trim reads on R2 (multi-cores)
# codes for flexbar version 3.4
# step3.1 trim TSO
time flexbar --adapter-min-overlap 7 --adapter-trim-end LEFT --adapters TSO.fa \
--min-read-length 16 --threads 24 \
--reads E8M_R1_extracted.clean.fq.gz \
--target E8M_R1_extracted_trimTSO.clean
# step3.2 trim polyA
time flexbar --adapter-min-overlap 7 --adapter-trim-end RIGHT --adapters adapters_polyAnT.fa \
--min-read-length 16 --threads 24 \
--reads E8M_R1_extracted_trimTSO.clean.fastq \
--target E8M_R1_extracted_trimTSO_trimPolyA.clean -z GZ
rm E8M_R1_extracted_trimTSO.clean.fastq

# codes for flexbar version 2.5
# step3.1 trim TSO
time flexbar --adapter-min-overlap 7 -ae LEFT -as AAGCAGTGGTATCAACGCAGAGTACATGGG \
--min-read-length 16 --threads 24 \
--reads E8M_R1_extracted.clean.fq.gz \
--target E8M_R1_extracted_trimTSO.clean
# step3.2 trim polyA
time flexbar --adapter-min-overlap 7 -ae RIGHT -a adapters_polyAnT.fa \
--min-read-length 16 --threads 24 \
--reads E8M_R1_extracted_trimTSO.clean.fq \
--target E8M_R1_extracted_trimOligo_trimPolyA.clean
rm E8M_R1_extracted_trimTSO.clean.fastq

# step4: STAR alignment (multi-cores)
STAR --runThreadN 24 \
--genomeDir ~/reference/mm10/STARIndexERCC/gencode.vM21 \
--readFilesIn E8M_R1_extracted_trimTSO_trimPolyA.clean.fastq.gz \
--readFilesCommand zcat \
--outFilterMultimapNmax 50 \
--outSAMtype BAM SortedByCoordinate \
--outFileNamePrefix E8M

# step5: Assign reads to: (multi-cores)
# step5.1 genes
time featureCounts \
-a ~/reference/mm10/Annotation/gencode.vM21.withERCC92.gtf \
--extraAttributes gene_id,gene_name,gene_type \
-T 24 \
-o E8M.gene_assigned \
-R BAM E8M.Aligned.sortedByCoord.out.dedup.bam
mv E8M.Aligned.sortedByCoord.out.dedup.bam.featureCounts.bam E8M.gene_assigned.bam
time samtools sort -@ 24 E8M.gene_assigned.bam -o E8M.gene_assigned.sorted.bam
time samtools index E8M.gene_assigned.sorted.bam
# step5.2 TEs
time featureCounts \
-a ~/reference/mm10/Annotation/mm10_rmsk_TE.gtf \
--extraAttributes gene_id,family_id,class_id \
-T 24 \
-o E8M.TE_assigned \
-R BAM E8M.Aligned.sortedByCoord.out.bam
mv E8M.Aligned.sortedByCoord.out.bam.featureCounts.bam E8M.TE_assigned.bam
time samtools sort -@ 24 E8M.TE_assigned.bam -o E8M.TE_assigned.sorted.bam
time samtools index E8M.TE_assigned.sorted.bam

# step6: Count UMIs per gene per cell (single-core)
# step6.1 for genes
time umi_tools count \
--per-gene --per-cell \
--gene-tag=XT --assigned-status-tag=XS \
-I E8M.gene_assigned.sorted.bam \
-S E8M.gene_counts.tsv.gz
# step6.2 for TE
time umi_tools count \
--per-gene --per-cell \
--gene-tag=XT --assigned-status-tag=XS \
-I E8M.TE_assigned.sorted.bam \
-S E8M.TE_counts.tsv.gz
```

### 其它问题

#### 1. STAR alignment的参数选择

**最终选择**：`--outFilterMultimapNmax 50`、`--winAnchorMultimapNmax 50`

> ​	这里主要是为了尽可能的保留`multi-mapped-reads`的同时又不至于降低序列比对的准确性。TEtranscripts这个工具的原始文献给出的参数是：
>
> --outFilterMultimapNmax 100 (default=10)
>
> --winAnchorMultimapNmax 100 (default=50)
>
> ​	我对自己的数据做了探索，遍历了一下第一个参数的条件。发现在--outFilterMultimapNmax 50的时候，基本上所有的multi-mapped-reads都会被保留了 (~99.98%)。

#### 2. 是否需要去除duplicates (umi_tools dedup)？

> ​	因为umi_tools count默认只统计不重复的UMI。因为目前无论是modified smart-seq2还是drop-based protocal，都是先扩增后断裂。因此map的坐标无法用来去重，重复的UMI意味着duplicates。因此，不需要进行dedup。

#### 3. mapping到基因组上的reads中真正能定量到基因上的有大比例？

![](https://raw.githubusercontent.com/JarningGau/blog_images/master/20190821/scRNA-seq-pipeline-02.png)

> ​	以一个96细胞的smart-seq2文库为例，有48%的reads assign到基因上，8%的reads assign到TE上，36%的reads因为是multi-mapping (有可能是来自于基因组的多拷贝区域，比如rDNA, tDNA等)，无法assign到任何feature上。这些reads总共占到了92%。剩下8%的reads属于要么mapping到的区域没有注释 (Unassigned_NoFeatures)，要么可能是重叠了多个feature (Unassigned_Ambiguity)。这些multi-mapping的reads仍然有可能来源于TEs，所以这里可能需要用`TEtranscripts`的`multi mode`来评估TEs的转录活性。