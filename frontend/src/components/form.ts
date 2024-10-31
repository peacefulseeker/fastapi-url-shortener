export class Form extends HTMLElement {
  private submitBtn: HTMLButtonElement;

  constructor() {
    super();

    this.submitBtn = this.querySelector(".btn") as HTMLButtonElement;
  }

  onSubmit = () => {
    this.submitBtn.classList.add("btn-form-submitting");
    setTimeout(() => {
      this.submitBtn.classList.remove("btn-form-submitting");
    }, 200);
  };
}

customElements.define("c-form", Form);
