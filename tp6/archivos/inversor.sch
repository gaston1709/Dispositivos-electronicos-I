v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 70 -80 70 -60 {lab=Vout}
N -10 -110 30 -110 {lab=Vin}
N -10 -110 -10 -30 {lab=Vin}
N -10 -30 30 -30 {lab=Vin}
N 70 -190 70 -140 {lab=Vdd}
N 70 0 70 50 {lab=Vss}
N -20 -70 -10 -70 {lab=Vin}
N 70 -70 120 -70 {lab=Vout}
N 70 -150 90 -150 {lab=Vdd}
N 70 -110 90 -110 {lab=Vdd}
N 90 -150 90 -110 {lab=Vdd}
N 70 -30 90 -30 {lab=Vss}
N 90 -30 90 20 {lab=Vss}
N 70 20 90 20 {lab=Vss}
N -30 -70 -20 -70 {lab=Vin}
N 120 -70 130 -70 {lab=Vout}
C {sky130_fd_pr/pfet_01v8.sym} 50 -110 0 0 {name=M2
W=2.1
L=0.15
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 50 -30 0 0 {name=M1
W=1.05
L=0.15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {ipin.sym} 70 -190 0 0 {name=p1 lab=Vdd
}
C {ipin.sym} 70 50 0 0 {name=p2 lab=Vss

}
C {ipin.sym} -30 -70 0 0 {name=p3 lab=Vin

}
C {opin.sym} 130 -70 0 0 {name=p4 lab=Vout
}
