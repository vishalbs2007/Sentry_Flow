# FlowSentry NS-2 topology: 4 clients -> R1 -> 4 servers
# Node ids (creation order): clients 0-3, router 4, servers 5-8
# Run:  ns flowsentry.tcl      (produces out.tr)
set ns [new Simulator]
set tf [open out.tr w]
$ns trace-all $tf

for {set i 0} {$i < 4} {incr i} { set c($i) [$ns node] }   ;# 0..3
set r [$ns node]                                            ;# 4
for {set i 0} {$i < 4} {incr i} { set s($i) [$ns node] }   ;# 5..8

for {set i 0} {$i < 4} {incr i} {
    $ns duplex-link $c($i) $r 10Mb 5ms DropTail
    $ns duplex-link $r $s($i) 10Mb 5ms DropTail
}

# ---- Flow 1: Web (TCP, bursty on/off Pareto, medium packets) ----
set tcp1 [new Agent/TCP];  set sink1 [new Agent/TCPSink]
$ns attach-agent $c(0) $tcp1;  $ns attach-agent $s(0) $sink1
$ns connect $tcp1 $sink1;      $tcp1 set fid_ 1
set web [new Application/Traffic/Pareto]
$web attach-agent $tcp1
$web set packetSize_ 500
$web set burst_time_ 300ms
$web set idle_time_ 1500ms
$web set rate_ 400k
$web set shape_ 1.5

# ---- Flow 2: VoIP (UDP, 160 B every 20 ms = 64 kbps, G.711-like) ----
set udp2 [new Agent/UDP];  set null2 [new Agent/Null]
$ns attach-agent $c(1) $udp2;  $ns attach-agent $s(1) $null2
$ns connect $udp2 $null2;      $udp2 set fid_ 2
set voip [new Application/Traffic/CBR]
$voip attach-agent $udp2
$voip set packetSize_ 160
$voip set interval_ 0.02

# ---- Flow 3: Streaming (UDP, 1200 B at ~2 Mbps, sustained) ----
set udp3 [new Agent/UDP];  set null3 [new Agent/Null]
$ns attach-agent $c(2) $udp3;  $ns attach-agent $s(2) $null3
$ns connect $udp3 $null3;      $udp3 set fid_ 3
set strm [new Application/Traffic/CBR]
$strm attach-agent $udp3
$strm set packetSize_ 1200
$strm set interval_ 0.0048
$strm set random_ 1

# ---- Flow 4: File transfer (TCP bulk FTP) ----
set tcp4 [new Agent/TCP];  set sink4 [new Agent/TCPSink]
$ns attach-agent $c(3) $tcp4;  $ns attach-agent $s(3) $sink4
$ns connect $tcp4 $sink4;      $tcp4 set fid_ 4
$tcp4 set packetSize_ 1000
set ftp [new Application/FTP]
$ftp attach-agent $tcp4

$ns at 1.0  "$web start"
$ns at 1.0  "$voip start"
$ns at 1.0  "$strm start"
$ns at 1.0  "$ftp start"
$ns at 61.0 "$web stop"
$ns at 61.0 "$voip stop"
$ns at 61.0 "$strm stop"
$ns at 61.0 "$ftp stop"
$ns at 62.0 "finish"

proc finish {} {
    global ns tf
    $ns flush-trace
    close $tf
    exit 0
}
$ns run
