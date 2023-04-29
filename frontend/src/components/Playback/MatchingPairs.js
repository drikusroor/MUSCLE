import React, {useRef} from "react";
import classNames from "classnames";

import PlayCard from "../PlayButton/PlayCard";

const MatchingPairs = ({
    playSection,
    sections,
    playerIndex,
    setPlayerIndex,
    lastPlayerIndex,
    finishedPlaying,
    stopAudioAfter,
    submitResult
}) => {
    const finishDelay = 1500;
    const xPosition = useRef(-1);
    const yPosition = useRef(-1);
    const score = useRef(undefined);

    const resultBuffer = useRef([]);

    const startTime = useRef(Date.now());
    
    const setScoreMessage = (score) => {

        switch (score) {       
            case -1: return '-1 <br />Misremembered';
            case 0: return '0 <br />No match';
            case 1: return '+1 <br />Lucky match';
            case 2: return '+2 <br />Good job!';
            default: return '';
        }
    }

    const registerUserClicks = (posX, posY) => {
        xPosition.current = posX;
        yPosition.current = posY;
    }

    const formatTime = (time) => {
        return time/1000;
    }

    const showFeedback = () => {        
        finishedPlaying();
        const turnedCards = sections.filter(s => s.turned);        
        sections.forEach(section => section.noevents = false);        
        if (turnedCards.length == 2) {
            sections.forEach(section => section.turned = false);            
            switch (score.current) {                                       
                case 1:
                    turnedCards[0].lucky = true;
                    turnedCards[1].lucky = true;
                    turnedCards[0].inactive = true;
                    turnedCards[1].inactive = true;                    
                    break;
                case 2:
                    turnedCards[0].memory = true;
                    turnedCards[1].memory = true;
                    turnedCards[0].inactive = true;
                    turnedCards[1].inactive = true;                    
                    break;
                default:
                    turnedCards[0].nomatch = true;
                    turnedCards[1].nomatch = true;
                    setTimeout(() => {
                        turnedCards[0].nomatch = false;
                        turnedCards[1].nomatch = false;                                               
                      }, 700);
                    break;  
            }
        }
    }


    const checkMatchingPairs = (index) => {
        const currentCard = sections[index];
        const turnedCards = sections.filter(s => s.turned);
        if (turnedCards.length < 2) {
            if (turnedCards.length == 1) {
                // we have two turned cards
                currentCard.turned = true;
                // set noevents for all but current
                sections.forEach(section => section.noevents = true);
                currentCard.noevents = false;
                // check for match
                const lastCard = lastPlayerIndex.current >= 0 ? sections[lastPlayerIndex.current] : undefined;                
                if (lastCard && lastCard.id === currentCard.id) {
                    // match                    
                    setPlayerIndex(-1);
                    if (currentCard.seen && lastCard.seen) {
                        score.current = 2;                        
                    } else {
                        score.current = 1;                        
                    }
                } else {
                    if (lastCard.seen && currentCard.seen) { score.current = -1; }
                    else { score.current = 0; }
                };                
            } else {
                // turn all cards back, turn current card
                lastPlayerIndex.current = -1;
                sections.forEach(section => section.turned = false);
                currentCard.turned = true;
                currentCard.noevents = true;
                score.current = undefined;
            }    
        } else {
            // second click on second card
            showFeedback();            
        }
        
        resultBuffer.current.push({
            selectedSection: currentCard.id,
            xPosition: xPosition.current,
            yPosition: yPosition.current,
            score: score.current,
            timestamp: formatTime(Date.now() - startTime.current)
        });
        
        currentCard.seen = true;

        if (sections.filter(s => s.inactive).length === sections.length) {
            // all cards have been turned
            setTimeout(() => {
                submitResult({moves: resultBuffer.current});
              }, finishDelay);
            
        }
        
        return;
    };

    const calculateRunningScore = () => {
        const allScores = resultBuffer.current.filter(
            r => r.score !== undefined ).map( r => r.score );
        if (!allScores.length) return 100;
        const initial = 0;
        const score = allScores.reduce( 
            (accumulator, s)  => accumulator + s, initial )
        return 100 + score; //Math.round(score / resultBuffer.current.length * 100)
    }
    
    return (
        <div className="aha__matching-pairs container">
            <div className="row">
                <div className="col-6">
                    <div dangerouslySetInnerHTML={{ __html: setScoreMessage(score.current) }}
                        className={classNames("matching-pairs__feedback", {
                            'fb-nomatch': score.current == 0,
                            'fb-lucky': score.current == 1,
                            'fb-memory': score.current == 2,
                            'fb-misremembered': score.current == -1
                        })}
                    />
                </div>
                <div className="col-6">
                    <div className="matching-pairs__score">Score: <br />{calculateRunningScore()}</div>        
                </div>
            </div>

            <div className="playing-board d-flex justify-content-center">
                {Object.keys(sections).map((index) => (
                    <PlayCard 
                        key={index}
                        onClick={()=> {
                            playSection(index);
                            checkMatchingPairs(index);
                        }}
                        registerUserClicks={registerUserClicks}
                        playing={playerIndex === index}
                        section={sections[index]}
                        onFinish={showFeedback}
                        stopAudioAfter={stopAudioAfter}                    
                    />
                )
                )}
            </div>
        </div>  
    )
}

export default MatchingPairs;