import jieba
import jieba.posseg as poss
from gensim.models import word2vec
from nltk.parse.stanford import StanfordDependencyParser
import os#, logging

#logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
#                    level=logging.INFO)

java_path = "D:/java/jdk/bin/java.exe"
os.environ['JAVAHOME'] = java_path

class SimComp:
    def get_sentence_list(self,sentence):
        OWL=list(jieba.cut(sentence)) #输出原始句子的原始分词
        return OWL

    def get_short_sentence_list(self,sentence): #输出仅包括动、名、行这三类词的分词列表
        words=poss.cut(sentence)
        s=[]
        for i in words:
            if ((i.flag[0]=='n'or i.flag[0]=='v' or i.flag[0]=='a')
                and len(i.word)>=2):
                s.append(i.word)
        return s

    def get_common_list(self,sentence1,sentence2): #输出公共词列表
        s1=self.get_short_sentence_list(sentence1)
        s2=self.get_short_sentence_list(sentence2)
        s=[i for i in s1 if i in s2]
        return s

    def get_common_chunk(self,sentence1,sentence2):
        CL1=self.get_short_sentence_list(sentence1)
        CL2=self.get_short_sentence_list(sentence2)
        clMatrix=[[0 for col in range(len(CL2))] for row in range(len(CL1))]
        ccList=[]
        for i in range(len(CL1)):
            for j in range(len(CL2)):
                if CL2[j]==CL1[i]:
                    clMatrix[i][j]=1
        i=0
        while i<len(CL1):
            j=0
            while j<len(CL2):
                if ((clMatrix[i][j]==1 and j!=len(CL2)-1) or (clMatrix[i][j]==1 and i!=len(CL1)-1)):
                    ccList.append('!')
                    while (i<len(CL1) and j<len(CL2)):
                        if (clMatrix[i][j]==1 and j!=len(CL2)-1 and i!=len(CL1)-1):
                              ccList.append(CL1[i])
                              i+=1
                              j+=1
                        elif(clMatrix[i][j]==1 and i!=len(CL1)-1 and j==len(CL2)-1):
                             ccList.append(CL1[i])
                             i+=1
                             j=0
                             break
                        elif(clMatrix[i][j]==1 and i==len(CL1)-1 and j!=len(CL2)-1 ):
                            ccList.append(CL1[i])
                            j+=1
                            break
                        elif(clMatrix[i][j]==1 and i==len(CL1)-1 and j==len(CL2)-1):
                            ccList.append(CL1[i])
                            j+=1
                            break
                        else:
                            j=0
                            break
                      #  '''
                elif(clMatrix[i][j]==1 and j==len(CL2)-1 and i==len(CL1)-1):
                    ccList.append('!')
                    ccList.append(CL1[i])
                    break
                    #'''
                else:
                    j+=1
            i+=1
        ccList='_'.join(ccList)
        ccList=ccList.split('_!_')
        ccList='!_'.join(ccList)
        ccList=ccList.split('!_')
        del ccList[0]
        return ccList
                

    def csim(self,k,sentence1,sentence2):#k是连续词加权系数
        c=self.get_common_chunk(sentence1,sentence2)
        c2=self.get_common_list(sentence1,sentence2)
        q=[]#q是c中各个元素包含词的个数
        q1=[]
        for i in c:
            if '_' in i:
               q.append(i.count('_')+1)
            else:
               q.append(1)
        for i in q:
            #if i==2:
               q1.append(i**k)
            #else:
             #  q1.append(1)
        if len(c2)==0:
            csim=0
        else:
            csim=sum(q1)/(len(c2)**k)
        return csim

    def get_index2(self,sentence1,sentence2):
        SL2=self.get_sentence_list(sentence2)
        CL=self.get_common_list(sentence1,sentence2)
        I2=[]
        i=0
        while i<len(SL2):
              j=0
              while j<len(CL):
                    if SL2[i]==CL[j]:
                       I2.append(CL.index(CL[j])+1)
                       CL[j]=0
                       break
                    j+=1
              i+=1
        return I2

    def osim(self,delta,sentence1,sentence2):
        I2=self.get_index2(sentence1,sentence2)
        punishment=[]
        normal=[]
        i=1
        for i in range(len(I2)-1):
            if I2[i]>I2[i+1]:
                Q=I2[i]-I2[i+1]
                punishment.append(delta**Q)
            else:
                normal.append(1)
        addpandn=punishment+normal
        if len(addpandn)==0:
            osim=1
        else:
           osim=sum(addpandn)/len(addpandn)
        return osim

    def get_first_uncommon_word_list(self,sentence1,sentence2):
        s1=self.get_sentence_list(sentence1)
        s=self.get_common_list(sentence1,sentence2)
        A=[]
        for i in s1:
            if i not in s:
                A.append(i)
        return A

    def get_second_uncommon_word_list(self,sentence1,sentence2):
        s2=self.get_sentence_list(sentence2)
        s=self.get_common_list(sentence1,sentence2)
        B=[]
        for i in s2:
            if i not in s:
                B.append(i)
        return B

    def dsim(self,sentence1,sentence2):
        model=word2vec.Word2Vec.load('d:\python\documents\yuliao\MyWord2VecModel')
        A=a.get_first_uncommon_word_list(sentence1,sentence2)
        B=a.get_second_uncommon_word_list(sentence1,sentence2)
        if (len(A)==0 or len(B)==0):
            dsim=1
        else:
         wsim=[[0 for col in range(len(B))] for row in range(len(A))]
         for i in range(len(A)):
            for j in range(len(B)):
                wsim[i][j]=model.similarity(A[i],B[j])
         dsim=0
         for i in range(len(A)):
            max_number=wsim[i][0]
            for j in range(1,len(B)):
                if wsim[i][j]>max_number:
                    max_number=wsim[i][j]
            dsim=(dsim+max_number)
         if len(A)==0:
            dsim=1
         else:
            dsim=dsim/len(A)
        return dsim

    def lsim(self,sentence1,sentence2):
        SL1=self.get_sentence_list(sentence1)
        SL2=self.get_sentence_list(sentence2)
        lsim=1-abs((len(SL1)-len(SL2))/(len(SL1)+len(SL2)))
        return lsim

    def minL(self,sentence1,sentence2):
        SSL1=self.get_short_sentence_list(sentence1)
        SSL2=self.get_short_sentence_list(sentence2)
        if len(SSL1)>len(SSL2):
            minL=len(SSL2)
        else:
            minL=len(SSL1)
        return minL

    def tsim(self,alpha,beta,gama,delta,k,sentence1,sentence2):
        csim=self.csim(k,sentence1,sentence2)
        dsim=self.dsim(sentence1,sentence2)
        minL=self.minL(sentence1,sentence2)
        lsim=self.lsim(sentence1,sentence2)
        osim=self.osim(delta,sentence1,sentence2)
        tsim=alpha*(csim*osim)+beta*dsim+gama*lsim
        return tsim

    def DependencyParmer(self,sentence):
        cutSentenceList=self.get_sentence_list(sentence)
        chi_parser = StanfordDependencyParser(r"D:\python\stanfordParser\jars\stanford-parser.jar",r"D:\python\stanfordParser\jars\stanford-parser-3.5.0-models.jar",r"D:\python\stanfordParser\jars\chinesePCFG.ser.gz")
        res = list(chi_parser.parse(cutSentenceList))
        relationship=[]
        for row in res[0].triples():
            relationship.append(row)
        return relationship

    def JudgepassiveFormat(self,sentence):
        relationship=self.DependencyParmer(sentence)
        for i in range(len(relationship)):
            if relationship[i][1]=='nsubjpass':
                return 'T'

    def JudgeCopFormat(self,sentence):
        relationship=self.DependencyParmer(sentence)
        for i in range(len(relationship)):
            if relationship[i][1]=='cop':
                return 'T'
                
    def ComponentExtraction(self,sentence):
        relationship=self.DependencyParmer(sentence)
        JudgePassiveFormat=self.JudgepassiveFormat(sentence)
        JudgeCopFormat=self.JudgeCopFormat(sentence)
        if JudgePassiveFormat=='T':
            for number in relationship:
                if number[1]=='nsubjpass':
                        sub=number[2][0]
                elif number[1]=='dobj':
                        obj=number[2][0]       
                elif number[1]=='auxpass':
                        pv=number[0][0]
                else:
                        obj=None           #因为dobj是最后一个元素,所以只要有dobj，就会覆盖原先给obj的None值。
        else:
           if JudgeCopFormat=='T':
              for number in relationship:
                  if number[1]=='cop':
                     pv=number[2][0]
                     obj=number[0][0]
                  elif number[1]=='nsubj':
                     sub=number[2][0]
           else:
               for number in relationship:
                    if number[1]=='dobj' or number[1]=='ccomp':
                      obj=number[2][0]
                      pv=number[0][0]
                    elif number[1]=='nsubj':
                       sub=number[2][0]
                   
        relationshipList=[]
        relationshipList.append(sub)
        relationshipList.append(pv)
        relationshipList.append(obj)
        return relationshipList

    def subSimilarity(self,sentence1,sentence2):
        model=word2vec.Word2Vec.load('d:\python\documents\yuliao\MyWord2VecModel')
        CE1=self.ComponentExtraction(sentence1)
        CE2=self.ComponentExtraction(sentence2)
        subSim=model.similarity(CE1[0],CE2[0])
        return subSim

    def objSimilarity(self,sentence1,sentence2):
        model=word2vec.Word2Vec.load('d:\python\documents\yuliao\MyWord2VecModel')
        CE1=self.ComponentExtraction(sentence1)
        CE2=self.ComponentExtraction(sentence2)
        if (CE1[2]!=None and CE2[2]!=None):
            objSim=model.similarity(CE1[2],CE2[2])
        else:
            objSim=0
        return objSim

    def pvSimilarity(self,sentence1,sentence2,p):
        model=word2vec.Word2Vec.load('d:\python\documents\yuliao\MyWord2VecModel')
        CE1=self.ComponentExtraction(sentence1)
        CE2=self.ComponentExtraction(sentence2)
        pvSim=model.similarity(CE1[1],CE2[1])
        
        if pvSim>p:
            pvSim=1
        else:
            pvSim=0

        return pvSim

    def ComponentSim(self,sentence1,sentence2,p):
        subSimilarity=self.subSimilarity(sentence1,sentence2)
        pvSimilarity=self.pvSimilarity(sentence1,sentence2,p)
        objSimilarity=self.objSimilarity(sentence1,sentence2)
        ComponentSim=0.3*subSimilarity+0.5*pvSimilarity+0.2*objSimilarity
        return ComponentSim

    def SimCombined(self,alpha,beta,gama,delta,k,sentence1,sentence2,p,m):
        ComponentSim=self.ComponentSim(sentence1,sentence2,p)
        tsim=self.tsim(alpha,beta,gama,delta,k,sentence1,sentence2)
        SimCombined=m*tsim+(1-m)*ComponentSim
        return SimCombined

'''
def get_document(file):
        sentence=[]
        OriginalSentence=open('d:\python\documents\Test_txtFiles\yun\one.txt',
                      'r',encoding='utf-8')
        for line in OriginalSentence.readlines():
            sentence.append(line.split(' '))

        sentenceString=sentence[0][0]

        c=sentenceString.count('。')
       #print(sentenceList1)
        #print(c)

        sentenceList=sentenceString.split('。')
        del(sentenceList[-1])
        return sentenceList
def sentence2()

'''        
            
        
        
            
               
        
    


s1='夏洛特公主喜欢滑雪'
s2='夏洛特公主喜爱滑雪'




a=SimComp()
alpha=0.5
beta=0.3
gama=0.2
delta=0.8
k=1.5
p=0.6
m=0.4
#print(a.get_short_sentence_list(s1))
#print(a.get_short_sentence_list(s2))
print(a.get_common_list(s1,s2))
print(a.DependencyParmer(s1))
print(a.DependencyParmer(s2))
#print(a.ComponentExtraction(s1))
#print(a.ComponentExtraction(s2))
print(a.get_common_chunk(s1,s2))
print('csim=',a.csim(k,s1,s2))
print('dsim=',a.dsim(s1,s2))
print('minL=',a.minL(s1,s2))
print('lsim=',a.lsim(s1,s2))
print('osim=',a.osim(delta,s1,s2))
print('tsim=',a.tsim(alpha,beta,gama,delta,k,s1,s2))
print('Component1=',a.ComponentExtraction(s1))
print('Component2=',a.ComponentExtraction(s2))
#print('subSimilarity:',a.subSimilarity(s1,s2))
print('pvSimilarity:',a.pvSimilarity(s1,s2,p))
#print('objSimilarity:',a.objSimilarity(s1,s2))
print('ComponentSim=',a.ComponentSim(s1,s2,p))
print('SimCombined=',a.SimCombined(alpha,beta,gama,delta,k,s1,s2,p,m))




        
        
