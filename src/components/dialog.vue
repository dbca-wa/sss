<template>
    <div class="{{classes}} reveal" id="userdialog" data-reveal data-close-on-click='false' > 
        <h3 v-show="title">{{title}}</h3>
        <div style="max-height:600px;" class="scroller">
        <div v-for="line in messages" class="row"  track-by="$index">
            <div v-for="message in line" class="small-{{message[1]}} columns {{messageClass(message)}}" track-by="$index" v-bind:style="messageAttr(message,'style')">
                 <div v-if="messageType(message) === 'show'" style="white-space:pre-wrap;">{{message[0]}}</div>
                 <a v-if="messageType(message) === 'link'" href="{{message[0]}}" @click.stop.prevent="utils.editResource($event)" target="{{messageAttr(message,'target')}}">{{message[0]}}</a>
                 <button v-if="messageType(message) === 'button'"  @click.stop.prevent="processEvent(message,'click')" :disabled="messageAttr(message,'disabled')" id="userdialog-button-{{message[0]}}">{{messageAttr("title")}}</button>
                 <img v-if="messageType(message) === 'img'"  @click.stop.prevent="processEvent(message,'click')" v-bind:src="message[0]"></img>
                 <input v-if="['radio','checkbox'].indexOf(messageType(message)) >= 0" type="{{message[2]['type']}}" name="{{messageAttr(message,'name')}}" value="{{message[0]}}" @click.stop="processEvent(message,'click',$event)" disabled="{{messageAttr(message,'disabled',false)}}" checked="{{isChecked(message)}}">
                 <input v-if="messageType(message) === 'text'" type="text" name="{{messageAttr(message,'name')}}"  disabled="{{messageAttr(message,'disabled')}}" value="{{getValue(message)}}">
            </div>
        </div>

        <div class="row align-center" v-if="isProgressBar">
            <div class="small-2 columns small-centered" >
                Total: {{tasks}}
            </div>

            <div class="small-2 columns small-centered" >
                Succeed: {{succeedTasks}}
            </div>

            <div class="small-2 columns small-centered" >
                Succeed: {{mergedTasks}}
            </div>

            <div class="small-2 columns small-centered" >
                Warning: {{warningTasks}}
            </div>

            <div class="small-2 columns small-centered" >
                Failed: {{failedTasks}}
            </div>

            <div class="small-2 columns small-centered" >
                Ignore: {{ignoredTasks}}
            </div>

            <div class="small-12 columns small-centered" >
                <div class="progress" role="progressbar" tabindex="0" aria-valuenow="{{completedTasks}}" aria-valuemin="0" aria-valuemax="{{tasks}}">
                    <div class="progress-meter" v-bind:style="fillstyle"></div>
                </div>
            </div>
        </div>
        </div>

        <div v-for="line in footer" track-by="$index" class="row"  >
            <br>
            <div v-for="message in revision && line" class="small-{{message[1]}} columns {{messageClass(message)}}" track-by="$index" v-bind:style="messageAttr(message,'style')">
                 <button v-if="messageType(message) === 'button'"  @click.stop.prevent="processEvent(message,'click')" :disabled="messageAttr(message,'disabled')" class="button" style="cursor:pointer" id="userdialog-button-{{message[0]}}">{{messageAttr(message,"title")}}</button>
                 <img v-if="messageType(message) === 'img'"  @click.stop.prevent="processEvent(message,'click')" v-bind:src="message[0]" style="cursor:pointer"></img>
                 <div v-if="messageType(message) === 'show'" style="white-space:pre-wrap;">{{message[0]}}</div>
                 <a v-if="messageType(message) === 'link'" href="{{message[0]}}" @click.stop.prevent="utils.editResource($event)" target="{{messageAttr(message,'target')}}">{{message[0]}}</a>
                 <input v-if="['radio','checkbox'].indexOf(messageType(message)) >= 0" type="{{message[2]['type']}}" name="{{messageAttr(message,'name')}}" value="{{message[0]}}" @click.stop="processEvent(message,'click',$event)" disabled="{{messageAttr(message,'disabled',false)}}" checked="{{isChecked(message)}}">
                 <input v-if="messageType(message) === 'text'" type="text" name="{{messageAttr(message,'name')}}"  disabled="{{messageAttr(message,'disabled')}}" value="{{getValue(message)}}">
            </div>
        </div>

        <button class="close-button" data-close aria-label="Close modal" type="button">
            <span aria-hidden="true">&times;</span>
        </button>
    </div>
</template>

<style>
#userdialog .button {
    padding-left:15px;
    padding-right:15px;
    margin-left:30px;
    margin-right:30px;
}
#userdialog .small-centered {
    text-align:center;
}
#userdialog .detail_name {
    font-weight:bold;
    text-align: right;
    padding-right:5px;
    background:white;
}
#userdialog .detail_value {
    text-align: left;
    padding-left:5px;
}
#userdialog .header {
    text-align: left;
    font-weight:bold;
}
</style>

<script>
  import { $,Vue,utils } from 'src/vendor.js'
  export default {
    data: function () {
      return {
        classes:"small",
        title:"",
        //[['msg',columnSize,'classes'],]
        //[['buttonvalue','buttontext','classes'],]
        tasks:null,
        succeedTasks:null,
        mergedTasks:null,
        failedTasks:null,
        warningTasks:null,
        ignoredTasks:null,
        callback:null,
        value:null,
        defaultValue:null,
        targetWindow:null,
        revision:1,

      }
    },
    computed: {
      loading: function () { return this.$root.loading },
      utils: function () { return this.$root.utils },
      hasFooter:function() {
        return this.footer.length > 0
      },
      isProgressBar:function() {
        return this.tasks > 0
      },
      completedTasks:function() {
        return this.succeedTasks + this.failedTasks + this.warningTasks + this.ignoredTasks
      },
      fillstyle:function() {
        return "width:" + (this.completedTasks / this.tasks) * 100 + "%"
      },
      messages:function() {
        return this.revision && this._messages
      },
      footer:function() {
        return this.revision && this._footer
      }

    },
    methods: {
      //options
      //title: dialog title
      //body: 
      // 1. string. 
      // 2. array of string 
      // 3. array of array of string or [message(string), columns,type(link, radio, checkbox,input,text(default),img,button), {element properies,event handlers,classes}  ]
      //footer:
      // 1. string. 
      // 2. array of string 
      // 3. array of array of string or [message(string), columns,type(link, radio, checkbox,input,text(default),img,button), {element properies,event handlers,classes}  ]
      //defaultOption: used if user close the dialog 
      //callback: called if user click one button or have a defaultOption
      show:function(options) {
        if (options === undefined) {
            $("#userdialog").foundation('open')
            return
        }
        var vm = this
        this.classes = options.classes || "small"
        this.title = options.title || ""
        this._messages.splice(0,this._messages.length)
        var messageLine = null
        if (Array.isArray(options.messages)) {
            $.each(options.messages,function(index,line){
                vm.addMessage(line)
            })
        } else {
            this._messages.push([[options.messages,12]])
        }
        if (Array.isArray(options.footer)) {
            $.each(options.footer,function(index,line){
                vm.addMessage(line,vm._footer)
            })
        } else {
            this._footer.push([[options.footer,12]])
        }
        this.callback = options.callback
        this.defaultOption = options.defaultOption === undefined?null:options.defaultOption
        this.option = null
        this.tasks = options.tasks
        this.succeedTasks = this.isProgressBar?0:null
        this.failedTasks = this.isProgressBar?0:null
        this.warningTasks = this.isProgressBar?0:null
        this.ignoredTasks = this.isProgressBar?0:null
        this.mergedTasks = this.isProgressBar?0:null
        this._initData = options.initData || null
        this._initFunc = options.initFunc || null
        this.revision += 1
        this.$nextTick(function(){
            if (vm._initFunc) {
                vm._initFunc()
            }
            $("#userdialog").foundation('open')
        })
      },
      close:function(button,handler) {
        if (button && button[2]["is_valid"]) {
            if (button[2]["is_valid"](button,this.getData()) === false) {
                return
            }
        }
        this.option = (button && button[0] !== undefined)?button[0]:this.defaultOption
        $("#userdialog").foundation('close')
      },
      rerend:function() {
        var messages = this._messages
        this._messages = []
        var footer = this._footer
        this._footer = []
        this.revision += 1
        var vm = this
        this.$nextTick(function(){
            vm._messages = messages
            vm._footer = footer
            vm.revision += 1
        })
      },
      //messages is optional, default is this.messages
      addMessage:function(message,messages) {
        messages = messages || this._messages
        messageLine = []
        messages.push(messageLine)
        if (Array.isArray(message)) {
            $.each(message,function(index,column){
                if (Array.isArray(column)) {
                    messageLine.push(column)
                } else {
                    messageLine.push([column,12])
                }
            })
        } else {
            messageLine.push([message,12])
        }
      },
      addSucceedTask:function() {
        this.succeedTasks += 1
      },
      addWarningTask:function() {
        this.warningTasks += 1
      },
      addFailedTask:function() {
        this.failedTasks += 1
      },
      addIgnoredTask:function() {
        this.ignoredTasks += 1
      },
      addMergedTask:function() {
        this.mergedTasks += 1
      },
      addTasks:function(newTasks) {
        this.tasks += newTasks
      },
      isLink:function(msg) {
        this._linkRe = this._linkRe || /^\s*https?\:\/\/.+/i
        return this._linkRe.test(msg)
      },
      messageAttr:function(msg,attr,defaultValue) {
        return (msg[2] && msg[2][attr])?msg[2][attr]:defaultValue
      },
      messageClass:function(msg) {
        return this.messageAttr(msg,"class","")
      },
      messageType:function(msg) {
        return this.messageAttr(msg,"type","show")
      },
      messageName:function(msg) {
        return this.messageAttr(msg,"name","")
      },
      getValue:function(msg) {
        if (this._initData && this.messageName(msg) in this._initData) {
            return this._initData[this.messageName(msg)]
        } else {
            return msg[0]
        }
      },
      isChecked:function(msg) {
        if (this._initData && this.messageName(msg) in this._initData) {
            value = this._initData[this.messageName(msg)]
            if (Array.isArray(value)) {
                return value.indexOf(msg[0])
            } else {
                return value === msg[0]
            }
        } else {
            return this.messageAttr(msg,"checked",false)
        }
      },
      getData:function(){
        result = {}
        $("#userdialog input").each(function(index){
            if ($(this).prop("disabled")) {
                //is disabled,ignore
                return
            } else if ( $(this).val().trim().length === 0) {
                //is empty,ignore
                return
            } else if ( ["radio","checkbox"].indexOf($(this).prop("type").toLowerCase()) >= 0 && !($(this).prop("checked")) ) {
                //is not checked
            } else if (!($(this).prop("name") in result)) {
                // is not in results
                result[$(this).prop("name")] = $(this).val().trim()
            } else if ( typeof result[$(this).prop("name")] === "string") {
                //is string value, change it to array
                result[$(this).prop("name")] = [result[$(this).prop("name")],$(this).val().trim()]
            } else {
                //is array value, append the new value
                result[$(this).prop("name")].push($(this).val().trim())
            }
        })
        return result
      },
      processEvent:function(message,event_key,ev) {
        var eventHandler = this.messageAttr(message,event_key)
        if (!eventHandler) {
            return
        } else if (eventHandler === "close") {
            this.close(message)
        } else {
            eventHandler.call(this,ev,message)
        }
      }
    },
    ready: function () {
      var vm = this
      this._messages = []
      this._footer = []
      var dialogStatus = this.loading.register("dialog","Dialog Component")
      dialogStatus.phaseBegin("initialize",100,"Initialize")

      $("#userdialog").on("open.zf.reveal",function(){
        $("#userdialog").css("top",Math.floor(($("#userdialog").parent().height() - utils.getHeight($("#userdialog"))) / 2) + "px" )
      })

      $("#userdialog").on("closed.zf.reveal",function(){
        vm._messages.splice(0,vm._messages.length)
        vm._footer.splice(0,vm._footer.length)
        vm.revision += 1
        if (vm.callback) {
            var value = ((vm.option === null || vm.option === undefined )?vm.defaultOption:vm.option)
            if (value !== null && value !== undefined) {
                vm.callback(value,vm.getData())
            }
            vm.callback = null
        }
      })

      dialogStatus.phaseEnd("initialize")
    }
  }
</script>
