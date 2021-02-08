-- @block Find a concept by string matching
select * 
  from 
    MRCONSO 
  where 
    STR='Atrial Fibrillation' 
    and LAT='ENG' 
    and SUPPRESS='N';

-- @block Find the preferred term and all synonyms given a CUI
select distinct STR 
  from MRCONSO 
  where 
    CUI='C0004238' 
    and LAT='ENG' 
    and SUPPRESS='N';

-- @block Find the ICD9CM code of ‘Atrial Fibrillation’

select distinct t2.CODE 
  from MRCONSO t1, MRCONSO t2
  where 
    t1.STR = 'Atrial Fibrillation'
    and t1.LAT='ENG'
    and t1.CUI=t2.CUI
    and t2.SAB='ICD9CM';

-- @block Find parents of C0004238 in SNOMEDCT_US
--    Using the MRREL table
select *
  from MRREL 
  where 
    CUI1='C0004238'  
    and REL='PAR' 
    and SAB='SNOMEDCT_US';

-- @block Find parents of C0004238 in SNOMEDCT_US
--    Using the MRHIER table
select *
  from MRHIER
  where 
    CUI='C0004238'
    and SAB='SNOMEDCT_US'
    and RELA='isa';


-- @block Normalize a term
select distinct b.* 
  from 
    MRCONSO a, 
    MRXNS_ENG b 
  where 
    a.str='children' 
    and a.SUI=b.SUI;

 
  