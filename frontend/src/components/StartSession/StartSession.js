import React, { useEffect } from "react";
import { createSession } from "../../API.js";
import Loading from "../Loading/Loading";

// StartSession is an experiment view that handles the creation of an experiment session
// - It only shows a loader screen while the session is created
// - This view is requird in every experiment as it created the session that is used for storing results
const StartSession = ({
    experiment,
    participant,
    playlist,
    setError,
    setSession,
    loadState,
}) => {
    // Create a new session, and set state to next_round
    useEffect(() => {
        const init = async () => {
            const data = await createSession({
                experiment,
                participant,
                playlist,
            });

            if (!data) {
                setError("Could not create a session");
                return;
            }

            // Store session
            setSession(data.session);

            // Start next round
            let newState = data.next_round.shift() //could reuse stateNextRound() in Experiment.js
            newState.next_round = data.next_round
            loadState(newState);

        };
        init();
    }, [experiment, participant, playlist, setError, setSession, loadState]);

    return <Loading loadingText={experiment.loading_text} />;
};

export default StartSession;
