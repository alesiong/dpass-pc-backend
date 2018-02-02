const components = [];

export default class Component {
  constructor(app) {
    this.app = app;
  }

  static register(ComponentType) {
    components.push(ComponentType);
  }

  static init(app) {
    components.forEach((C) => { new C(app); });
  }
}
