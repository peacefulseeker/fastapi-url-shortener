export enum ToastLevel {
  SUCCESS = "success",
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
}

export class Toast extends HTMLElement {
  private toast: HTMLDivElement;
  private alert: HTMLDivElement;
  private close: HTMLSpanElement;
  private message: HTMLSpanElement;
  private level: ToastLevel = ToastLevel.SUCCESS;
  private ttl: number | undefined;

  constructor() {
    super();
    this.toast = this.querySelector("#toast") as HTMLDivElement;
    this.alert = this.querySelector("#toast-alert") as HTMLDivElement;
    this.message = this.querySelector("#toast-message") as HTMLSpanElement;
    this.close = this.querySelector("#toast-close") as HTMLSpanElement;

    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.close.addEventListener("click", this.hide);
    document.addEventListener("click", this.onOutsideClick);
    document.addEventListener("touchstart", this.onOutsideClick);
  }

  private onOutsideClick = (event: Event) => {
    if (!this.toast.contains(event.target as Node)) {
      this.hide();
    }
  };

  show(message: string, toastLevel: ToastLevel, lifeSpan: number | null = 3000) {
    this.clearAlert();

    this.message.innerHTML = message.trim().replace("\n", "");
    this.level = toastLevel;
    this.alert.classList.add(`alert-${toastLevel}`);
    this.toast.classList.add("toast-visible");

    if (lifeSpan) {
      this.ttl = setTimeout(() => {
        this.hide();
      }, lifeSpan);
    }
  }

  clearAlert() {
    clearTimeout(this.ttl);
    this.alert.classList.remove(`alert-${this.level}`);
  }

  hide = () => {
    this.toast.classList.remove("toast-visible");
  };
}

customElements.define("c-toast", Toast);
