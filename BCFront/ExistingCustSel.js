export default {
  // HTML structure of componenet
  template: `
    <div>
      <p>Existing Customer Name Select {{msg}}:</p>
    </div>
  `,

  // passing data from parent component
  props: [
    'cur_cust'
  ],

  data() {
    return {
      msg2: 'dude'
    }
  }
}
