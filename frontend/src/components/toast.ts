export enum ToastLevel {
  SUCCESS = "success",
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
}

export class Toast extends HTMLDivElement {
  private alert: HTMLDivElement;
  private close: HTMLSpanElement;
  private message: HTMLSpanElement;
  private level: ToastLevel = ToastLevel.SUCCESS;
  private ttl: number | undefined;

  constructor() {
    super();

    this.alert = this.querySelector("#toast-alert") as HTMLDivElement;
    this.message = this.querySelector("#toast-message") as HTMLSpanElement;
    this.close = this.querySelector("#toast-close") as HTMLSpanElement;
  }

  connectedCallback() {
    this.close.addEventListener("click", this.hide.bind(this));
    document.addEventListener("click", this.onOutsideClick.bind(this));
    document.addEventListener("touchstart", this.onOutsideClick.bind(this));
  }

  disconnectedCallback() {
    this.close.removeEventListener("click", this.hide.bind(this));
    document.removeEventListener("click", this.onOutsideClick.bind(this));
    document.removeEventListener("touchstart", this.onOutsideClick.bind(this));
  }

  onOutsideClick(event: Event) {
    if (!this.contains(event.target as Node)) {
      this.hide();
    }
  }

  show(message: string, toastLevel: ToastLevel, lifeSpan: number | null = 3000) {
    this.clearAlert();

    this.message.innerHTML = message.replace(/\s\s+/g, "");
    this.level = toastLevel;
    this.alert.classList.add(`alert-${toastLevel}`);
    this.classList.add("toast-visible");

    if (lifeSpan) {
      this.ttl = setTimeout(this.hide, lifeSpan);
    }
  }

  clearAlert() {
    clearTimeout(this.ttl);
    this.alert.classList.remove(`alert-${this.level}`);
  }

  hide() {
    this.classList.remove("toast-visible");
  }
}

customElements.define("c-toast", Toast, { extends: "div" });
