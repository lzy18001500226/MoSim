import { Route, Switch } from "wouter";

import AuthPage from "./pages/auth";
import ChatPage from "./pages/app/chat";
import SetupPage from "./pages/setup";

import AppSidebar from "./components/sidebar";
import { AuthGuard } from "./provider/auth-provider";

import ModelProviderPage from "./pages/app/settings/model-provider";

const App = () => (
  <>
    {/*
      Routes below are matched exclusively -
      the first matched route gets rendered
    */}
    <Switch>
      <Route path="/setup" component={SetupPage} />
      <Route path="/auth" component={AuthPage} />

      <AppSidebar>
        <AuthGuard>
          <Route path="/app" nest>
            <Route path="/" component={ChatPage} />
            <Route path="/c/:id" component={(id) => <ChatPage />} />
          </Route>
        </AuthGuard>
        <AuthGuard>
          <Route path="/dashboard" nest>
            <Route path="/models" nest>
              <Route path="/orders" />
            </Route>
            <Route path="/settings" nest>
              <Route path="/model-provider" component={ModelProviderPage} />
            </Route>
          </Route>
        </AuthGuard>
      </AppSidebar>

      {/* Default route in a switch */}
      <Route>404: No such page!</Route>
    </Switch>
  </>
);

export default App;
