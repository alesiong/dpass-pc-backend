// @flow

export type App = Object;
const components: Array<Class<Component>> = [];

export default class Component {
  app: App;

  constructor(app: App) {
    this.app = app;
  }

  static register(ComponentType: Class<Component>) {
    components.push(ComponentType);
  }

  static init(app: App) {
    components.forEach((C) => {
      new C(app);
    });
  }
}
