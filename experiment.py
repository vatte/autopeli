from autopeli import *

def runExperiment():

    send_event(100)
    core.wait(1.995)

    send_event(100)
    core.wait(1.995)

    send_event(100)
    core.wait(1.995)

    send_event(100)
    core.wait(1.995)

    send_event(100)
    core.wait(1.995)

    show_fixation(120)

    setDriver(1)
    send_event(101)
    runTrack('Track1')

    show_fixation(5)
    setDriver(2)
    send_event(201)
    runTrack('Track1')

    show_fixation(5)
    setDriver(1)
    send_event(102)
    runTrack('Track2')

    show_fixation(5)
    setDriver(2)
    send_event(202)
    runTrack('Track2')

    show_fixation(5)
    setDriver(1)
    send_event(103)
    runTrack('Track3')

    show_fixation(5)
    setDriver(2)
    send_event(203)
    runTrack('Track3')

    show_fixation(5)
    setDriver(1)
    send_event(104)
    runTrack('Track4')

    show_fixation(5)
    setDriver(2)
    send_event(204)
    runTrack('Track4')

    send_event(255)

    show_fixation(5)
