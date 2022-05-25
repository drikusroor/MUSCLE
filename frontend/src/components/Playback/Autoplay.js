import React, { useState, useEffect } from "react";

import * as audio from "../../util/audio";
import { MEDIA_ROOT } from "../../config";

import Circle from "../Circle/Circle";
import ListenCircle from "../ListenCircle/ListenCircle";
import Preload from "../Preload/Preload";

const PRELOAD = "PRELOAD";
const RECOGNIZE = "RECOGNIZE";


const AutoPlay = ({instruction, preloadMessage, playConfig, sections, time, startedPlaying, finishedPlaying, submitResult, autoAdvance, decisionTime, className=''}) => {
    // player state
    const [state, setState] = useState({ view: PRELOAD });
    const [running, setRunning] = useState(playConfig.auto_play);
    const setView = (view, data = {}) => {
        setState({ view, ...data });
    }

    const section = sections[0];

    const onCircleTimerTick = (t) => {
        time.current = t;
    };


     // Handle view logic
     useEffect(() => {
         switch (state.view) {
             case RECOGNIZE:
                 // Play audio at start time            
                 if (!playConfig.mute) {
                     audio.playFrom(Math.max(0, playConfig.playhead));
                 }
                 startedPlaying();
                 break;
             default:
             // nothing
         }

         // Clean up
         return () => {
             audio.pause();
         };
     }, [state, playConfig]);


    // Render component based on view
    switch (state.view) {
        case PRELOAD:           
            return (
                <Preload
                    instruction={preloadMessage}
                    duration={playConfig.ready_time}
                    url={MEDIA_ROOT + section.url}
                    onNext={() => {                        
                        setView(RECOGNIZE);
                    }}
                />
            );
        case RECOGNIZE:            
            return (
                <div>
                    <div className="circle">
                        <Circle
                            running={running}
                            duration={decisionTime}
                            color="white"
                            animateCircle={playConfig.show_animation}
                            onTick={onCircleTimerTick}
                            onFinish={() => {
                                // Stop audio
                                finishedPlaying();
                            }}
                        />
                        <div className="circle-content">
                            {playConfig.show_animation
                                ? <ListenCircle
                                    duration={decisionTime}
                                    histogramRunning={running}
                                    countDownRunning={running}
                                />
                                : <div className="stationary">
                                    <span className="ti-headphone"></span>
                                </div>
                            }
                        </div>
                    </div>
                    <div className={
                        "aha__listen d-flex flex-column justify-content-center align-items-center " +
                        className
                    }
                    >
                    {/* Instruction */}
                    {instruction && (<div className="instruction d-flex justify-content-center align-items-center">
                        <h3 className="text-center">{instruction}</h3>
                    </div>)}
                </div>
            </div>
            )
            default:
                return <div>Unknown view: {state.view}</div>;
        }
}
export default AutoPlay;
