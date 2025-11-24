v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
B 2 -388 284 412 684 {flags=graph,unlocked
y1=-1
y2=5
ypos1=0
ypos2=2
divy=5
subdivy=4
unity=1
x1=3.4957626e-10
x2=1.0349566e-08
divx=5
subdivx=4
xlabmag=1.0
ylabmag=1.0
node="in
out"
color="4 5"
dataset=-1
unitx=1
logx=0
logy=0
autoload=1
sim_type=tran
rainbow=0
rawfile=$netlist_dir/std_not4_tb.raw}
N -420 -30 -420 30 {lab=GND}
N -420 30 -330 30 {lab=GND}
N -40 -10 -40 30 {lab=GND}
N -140 30 -40 30 {lab=GND}
N -40 -90 -20 -90 {lab=out}
N -20 -180 -20 -90 {lab=out}
N -320 -140 -320 30 {lab=GND}
N -380 -80 -380 30 {lab=GND}
N -380 -160 -380 -150 {lab=in}
N -380 -160 -320 -160 {lab=in}
N -420 -180 -320 -180 {lab=#net1}
N -330 30 -320 30 {lab=GND}
N -320 30 -230 30 {lab=GND}
N -230 30 -140 30 {lab=GND}
N -380 -90 -380 -80 {lab=GND}
N -40 -90 -40 -70 {lab=out}
N -420 -180 -420 -90 {lab=#net1}
C {sky130_fd_pr/corner.sym} 90 -290 0 0 {name=CORNER only_toplevel=true corner=tt}
C {simulator_commands_shown.sym} 190 -50 0 0 {name=s1
value="
.control
tran 0.5n 40n
write std_not4_tb.raw
.endc
.save all
"}
C {vsource.sym} -420 -60 0 0 {name=V1 value=1.8 savecurrent=false}
C {vsource.sym} -380 -120 0 0 {name=V2 value="PULSE(0 1.8 0 1n 1n 5n 10n 4)" savecurrent=false}
C {gnd.sym} -230 30 0 0 {name=l1 lab=GND}
C {res.sym} -40 -40 0 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} -380 -150 0 0 {name=p1 sig_type=std_logic lab=in
}
C {lab_pin.sym} -20 -90 0 1 {name=p2 sig_type=std_logic lab=out
}
C {/home/gaston/Documents/inversor.sym} -170 -160 0 0 {name=x1}
