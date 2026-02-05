import matplotlib.pyplot as plt

beginMark='Per MPI'
endMark='Loop time'

def read(logf):
    with open(logf) as f:
        d=f.read()
    
    take=False
    d=d.split('\n')
    fields=[]
    arr=None
    fld=None
    
    for s in d:
        s=s.strip()
        
        if s.find(beginMark) == 0:
            take=True
            continue
        
        if s.find(endMark) == 0:
            take=False
            continue
        
        if not take:
            continue
        
        s=s.split()
        
        if not fld:
            fld=s
            continue
            
        try:
            eval(s[0])
        except:
            continue
        
        nfield=len(s)
        
        if arr == None:
            arr=[]
            for a in range(nfield):
                arr.append([])
        
        for a in range(nfield):
            arr[a].append(eval(s[a]))
        
    return arr,fld

def readic(logf):
    d,f=read(logf)
    g={}
    for i in range(len(f)):
        g[f[i]]=d[i]
    
    return g

def plot(arr, fields, show=True, opt=[]):
    if type(arr) == str:
        arr,fld=read(arr)
    xx,yy=[],[]
    xl,yl='x','y'

    if type(fields[0]) == str:
        for i in range(len(fld)):
            if fld[i] == fields[0]:
                xx=arr[i]
                xl=fld[i]
                break
    else:
        xx=arr[fields[0]]
        xl=fld[fields[0]]

    if type(fields[1]) == str:
        for i in range(len(fld)):
            if fld[i] == fields[1]:
                yy=arr[i]
                yl=fld[i]
                break
    else:
        yy=arr[fields[1]]
        yl=fld[fields[1]]

    plt.plot(xx,yy)
    plt.xlabel(xl)
    plt.ylabel(yl)
    
    for o in opt:
        eval('plt.'+o)
        
    if show:
        plt.show()

def read_lmp(fname):
    with open(fname) as fl:
        ss=fl.read().split('\n')
    
    rec={}
    
    for i in range(len(ss)):
        s=ss[i].strip()
        if s.find('#') == 0: continue
        if s.find('atoms') > 0:
            na=eval(s.split()[0])
            rec['natoms']=na
        elif s.find('atom types') >0:
            nty=eval(s.split()[0])
            rec['ntypes']=nty
        elif s.find('xlo xhi') > 0:
            s=s.split()
            rec['xbox']=(float(s[0]),float(s[1]))
        elif s.find('ylo yhi') > 0:
            s=s.split()
            rec['ybox']=(float(s[0]),float(s[1]))
        elif s.find('zlo zhi') > 0:
            s=s.split()
            rec['zbox']=(float(s[0]),float(s[1]))
            
        elif s.find('Masses') == 0:
            i+=2
            rec['masses']=nty*[0]
            while ss[i] != '':
                st=ss[i].split()
                mi=int(st[0])-1
                rec['masses'][mi]=float(st[1])
                i+=1
            continue
            
        elif s.find('Atoms') == 0:
            i+=2
            if s.find('# charge'):
                rec['id']=[]
                rec['type']=[]
                rec['charge']=[]
                rec['x']=[]
                rec['y']=[]
                rec['z']=[]
                while ss[i] != '':
                    d=ss[i].split()
                    rec['id'].append(int(d[0]))
                    rec['type'].append(int(d[1]))
                    rec['charge'].append(float(d[2]))
                    rec['x'].append(float(d[3]))
                    rec['y'].append(float(d[4]))
                    rec['z'].append(float(d[5]))
                    i+=1
                    if i>=len(ss): break
            else:
                rec['id']=[]
                rec['type']=[]
                rec['x']=[]
                rec['y']=[]
                rec['z']=[]
                while ss[i] != '':
                    d=ss[i].split()
                    rec['id'].append(int(d[0]))
                    rec['type'].append(int(d[1]))
                    rec['x'].append(float(d[2]))
                    rec['y'].append(float(d[3]))
                    rec['z'].append(float(d[4]))
                    i+=1
                    if i>=len(ss): break
            continue
            
        elif s.find('Velocities') == 0:
            rec['vx']=[]
            rec['vy']=[]
            rec['vz']=[]            
            for iv in range(i+2,na+(i+2)):
                s=[ float(b) for b in ss[iv].split()[1:] ]
                rec['vx'].append(s[0])
                rec['vy'].append(s[1])
                rec['vz'].append(s[2])

    return rec

def write_lmp(data,oname=None,resetid=True):

    xmax,ymax,zmax=-1e6,-1e6,-1e6
    xmin,ymin,zmin=1e6,1e6,1e6
    massmap=None
    typemap=None
    
    natoms=len(data['x'])
    nty=data['ntypes']

    for i in range(natoms):
        a=[data['x'][i],data['y'][i],data['z'][i]]
        if xmax<a[0]: xmax=a[0]
        if ymax<a[1]: ymax=a[1]
        if zmax<a[2]: zmax=a[2]
        if xmin>a[0]: xmin=a[0]
        if ymin>a[1]: ymin=a[1]
        if zmin>a[2]: zmin=a[2]
    
    if 'xbox' in data: # make sure that all atoms are included. larger box always accepted.
        if data['xbox'][0] < xmin: xmin=data['xbox'][0]
        if data['xbox'][1] > xmax: xmax=data['xbox'][1]
        if data['ybox'][0] < ymin: ymin=data['ybox'][0]
        if data['ybox'][1] > ymax: ymax=data['ybox'][1]
        if data['zbox'][0] < zmin: zmin=data['zbox'][0]
        if data['zbox'][1] > zmax: zmax=data['zbox'][1]    
    
    if 'types' in data:
        typemap=data['types']
    else:
        typemap={}
        for t in range(1,nty+1):
            typemap[t]=t

    if not 'type' in data:
        data['type']=[]
        for i in range(natoms):
            data['type'].append(1)
    
    slmp="# LAMMPS data file written by guriang lammps tool (122021)\n"
    slmp+="%d atoms\n"%(natoms)
    slmp+="%d atom types\n"%(nty)
    slmp+="%f %f xlo xhi\n"%(xmin,xmax)
    slmp+="%f %f ylo yhi\n"%(ymin,ymax)
    slmp+="%f %f zlo zhi\n\n"%(zmin,zmax)
    
    if 'masses' in data:
        if len(data['masses']) != nty:
            print('inconsistet mass setting, %d masses required'%nty)
            return
        
        slmp+="Masses\n\n"
        for m in range(len(data['masses'])):
            slmp+="%d %f\n"%(m+1,data['masses'][m])
        slmp+="\n"
    
    if 'charge' in data:
        slmp+="Atoms # charge\n\n"
    else:
        slmp+="Atoms\n\n"
    
    aid=1
    for i in range(natoms):
        if 'charge' in data:
            a=[data['type'][i],data['charge'][i],data['x'][i],data['y'][i],data['z'][i]]
            a[0]=typemap[a[0]]
            slmp+="%d %d %f %f %f %f\n"%(aid,a[0],a[1],a[2],a[3],a[4])
        else:
            a=[data['type'][i],data['x'][i],data['y'][i],data['z'][i]]
            a[0]=typemap[a[0]]
            slmp+="%d %d %f %f %f\n"%(aid,a[0],a[1],a[2],a[3])
        aid+=1
    
    if 'vx' in data:
        slmp+='\nVelocities\n\n'
        for i in range(natoms):
            slmp+="%d %f %f %f\n"%(i+1,data['vx'][i],data['vy'][i],data['vz'][i])

    
    if oname:
        with open(oname,'w') as lmpfl:
            lmpfl.write(slmp)
        print("LAMMPS data created: ", oname)
    else:
        print(slmp)

def read_xyz(fname):
    with open(fname,'r') as fl:
        xx=fl.read().split('\n')

    na=eval(xx[0])
    info=xx[1]
    rec={
        'natoms':na,
        'info':info,
        'ntypes': 0,
        'type':[],
        'x':[],
        'y':[],
        'z':[]
    }
    tc={}
    for i in range(2,na+2):
        if xx[i] == '':
            continue
        a=xx[i].split()
        ty=a[0]
        a=[ float(x) for x in a[1:] ]
        tc[ty]=1
        rec['type'].append(ty)
        rec['x'].append(a[0])
        rec['y'].append(a[1])
        rec['z'].append(a[2])
    
    cnt=1
    for i in tc:
        tc[i]=cnt
        cnt+=1
    
    rec['ntypes']=len(tc)
    rec['types']=tc
    
    return rec

def write_xyz(data,fname=None):
    sx='%d\n\n'%len(data['x']) # do not trust natoms variable
    for i in range(data['natoms']):

        if 'types' in data:
            if data['type'][i] in data['types']:
                sx+='{} '.format(data['types'][data['type'][i]])
            else:
                sx+='{} '.format(data['type'][i])
        else:
             sx+='{} '.format(data['type'][i])

        sx+='%f %f %f\n'%(data['x'][i],data['y'][i],data['z'][i])
    
    if fname:
        with open(fname,'w') as ff:
            ff.write(sx)
    else:
        print(sx)

def convert(fname,oname,typemap,massmap=None,charge=True,reserve_type=0):
    # convert from xyz to lmpdata
    atoms=read_xyz(fname)
    atoms['types']=typemap
    nty=1
    
    for i in typemap:
        if nty<typemap[i]: 
            nty=typemap[i]
    
    if reserve_type>nty:
        nty=reserve_type
    
    atoms['ntypes']=nty
    
    if massmap:
        atoms['masses']=massmap
        
    if charge:
        atoms['charge']=[]
        for i in range(atoms['natoms']):
            atoms['charge'].append(0.0)
    
    # todo: dig bounding box from info line
    write_lmp(atoms,oname,charge)
