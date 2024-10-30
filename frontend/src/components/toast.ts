export enum ToastLevel {
  SUCCESS = "success",
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
}

export class Toast extends HTMLElement {
  private toast: HTMLDivElement;
  private alert: HTMLDivElement;
  private message: HTMLSpanElement;
  private level: ToastLevel = ToastLevel.SUCCESS;
  private lifeSpan: number = 3000;
  private ttl: number | undefined;

  constructor() {
    super();
    this.toast = this.querySelector("#toast") as HTMLDivElement;
    this.alert = this.querySelector("#toast-alert") as HTMLDivElement;
    this.message = this.querySelector("#toast-message") as HTMLSpanElement;
  }

  show(message: string, toastLevel: ToastLevel) {
    this.clearAlert();

    this.level = toastLevel;
    this.alert.classList.add(`alert-${toastLevel}`);
    this.toast.classList.add("opacity-100");
    this.message.innerHTML = message;
    this.ttl = setTimeout(() => {
      this.hide();
    }, this.lifeSpan);
  }

  clearAlert() {
    clearTimeout(this.ttl);
    this.alert.classList.remove(`alert-${this.level}`);
  }

  hide() {
    this.toast.classList.remove("opacity-100");
  }
}

customElements.define("c-toast", Toast);
