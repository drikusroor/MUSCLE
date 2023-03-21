import React, {useRef} from "react";
import { getCurrentTime } from "../../util/audio";

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
    const xPosition = useRef(-1);
    const yPosition = useRef(-1);
    const score = useRef(-1);

    const resultBuffer = useRef([]);

    const startTime = useRef(Date.now());

    const setScoreMessage = (score) => {
        switch(score) {
            case 0: return 'No match! 0 points';
            case 1: return 'Lucky match! +1 points';
            case 2: return 'Good memory! +2 points';
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

    const checkMatchingPairs = (index) => {
        const currentCard = sections[index];
        const turnedCards = sections.filter(s => s.turned);
        if (turnedCards.length == 1) {
            // we have two turned cards
            currentCard.turned = true;
            // check for match
            const lastCard = lastPlayerIndex.current >=0 ? sections[lastPlayerIndex.current] : undefined;
            if (lastCard && lastCard.id === currentCard.id) {
                // match
                lastCard.inactive = true;
                currentCard.inactive = true;
                setPlayerIndex(-1);
                if (currentCard.seen && lastCard.seen) {
                    score.current = 2;
                } else {
                    score.current = 1;
                }
            } else { score.current = 0; };
        } else {
            // turn all cards back, turn current card
            lastPlayerIndex.current = -1;
            sections.forEach(section => section.turned = false);
            currentCard.turned = true;
            score.current = undefined;
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
            submitResult({moves: resultBuffer.current});
        }
        
        return;
    };

    const calculateRunningScore = () => {
        const allScores = resultBuffer.current.filter(
            r => r.score >= 0 ).map( r => r.score );
        if (!allScores.length) return 0;
        const initial = 0;
        const score = allScores.reduce( 
            (accumulator, s)  => accumulator + s, initial )
        return Math.round(score / resultBuffer.current.length * 100)
    }
    
    return (
        <div
            className={classNames(
                "aha__matching_pairs d-flex justify-content-around",
                "player-count-" + sections.length
            )}
        >
            <div className="running-score">
                Your score: {calculateRunningScore()}
                {" "}n: {sections.filter(s => !s.inactive).length / 2}
                {" "}p: {sections.filter(s => s.inactive).length / 2}
                {" "}k: {sections.filter(s => s.seen).length}
            </div>
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
                onFinish={finishedPlaying}
                stopAudioAfter={stopAudioAfter}
                />
            )
            )}
            <div className="feedback">{setScoreMessage(score.current)}</div>
        </div>  
    )
}

export default MatchingPairs;