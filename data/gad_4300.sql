drop schema gad;
create schema gad;
use  gad;

drop table diseases;
create table diseases(
diseaseId varchar(20) primary key not null,
diseaseName varchar(500) not null,
diseaseType	varchar(10),
diseaseClass varchar(50), 	
diseaseSemanticType	varchar(100),
NofGenes int,
NofPmids int);

drop table genes;
create table genes(
geneId int primary key not null,
geneSymbol varchar(15) not null,	
DSI	decimal(10,2),
DPI	decimal(10,2),
PLI	decimal(10,2),
protein_class_name varchar(200),
protein_class varchar(20),
NofDiseases	int,
NofPmids int
);

drop table gad;
create table gad(
geneId int not null,
diseaseId varchar(20) not null,
score decimal(10,2) not null,
ei decimal(10,2) not null,
el varchar(20),
yearInitial int,
yearFinal int,
g_source varchar(15),
primary key(geneId, diseaseId),
foreign key (geneId) references genes(geneId),
foreign key (diseaseId) references diseases(diseaseId)
);

