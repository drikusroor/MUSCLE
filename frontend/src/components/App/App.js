import React from "react";
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Redirect,
} from "react-router-dom";
import { URLS, EXPERIMENT_SLUG } from "../../config";
import Experiment from "../Experiment/Experiment";
import Profile from "../Profile/Profile";
import StoreProfile from "../StoreProfile/StoreProfile.js";

// App is the root component of our application
const App = () => {
    return (
        <Router className="aha__app">
            <Switch>
                {/* Default experiment */}
                <Route path="/" exact>
                    <Redirect
                        to={URLS.experiment.replace(":slug", EXPERIMENT_SLUG)}
                    />
                </Route>

                {/* Experiment */}
                <Route path={URLS.experiment} component={Experiment} />

                {/* Profile */}
                <Route path={URLS.profile} exact>
                    <Profile slug={EXPERIMENT_SLUG} />
                </Route>

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
