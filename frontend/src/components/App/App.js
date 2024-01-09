import {useEffect, React} from "react";
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Redirect
} from "react-router-dom";
import { create } from "zustand";
import { EXPERIMENT_SLUG, URLS } from "../../config";
import { getParticipant } from "API";
import Experiment from "../Experiment/Experiment";
import Profile from "../Profile/Profile";
import Reload from "../Reload/Reload";
import StoreProfile from "../StoreProfile/StoreProfile.js";

export const useParticipantStore = create((set) => ({
    participant: null,
    setParticipant: (participant) => set((state) => ({participant}))
}));

// App is the root component of our application
const App = () => {
    const setParticipant = useParticipantStore((state) => state.setParticipant);
    const queryParams = window.location.search;
    
    useEffect(() => {
        if (queryParams && !(new URLSearchParams(queryParams).has("participant_id"))) {
            console.error("Unknown URL parameter, use ?participant_id=")
            return;
        }
        getParticipant(queryParams).then(data => {
            setParticipant(data);
        })
    }, [])

    return (
        <Router className="aha__app">
            <Switch>
                {/* Request reload for given participant */}
                <Route path={URLS.reloadParticipant}>
                    <Reload/>
                </Route>

                {/* Default experiment */}
                <Route path="/" exact>
                    <Redirect
                        to={URLS.experiment.replace(":slug", EXPERIMENT_SLUG)}
                    />
                </Route>
                
                {/* Profile */}
                <Route path={URLS.profile} exact>
                    <Profile slug={EXPERIMENT_SLUG} />
                </Route>

                {/* Experiment */}
                <Route path={URLS.experiment} component={Experiment} />

                <Route path={URLS.session} />

                {/* Store profile */}
                <Route
                    path={URLS.storeProfile}
                    exact
                    component={StoreProfile}
                />


            </Switch>
        </Router>
    );
};

export default App;
