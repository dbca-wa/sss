<template>
  <div class="tabs-panel" id="weatheroutlook" v-cloak>
    <div class="row" >
      <div class="columns">
        <div class="tabs-content vertical" data-tabs-content="setting-tabs">
          <div id="weatheroutlook-settings">

            <div class="tool-slice row collapse">
                <div class="small-12">
                    <label style="font-weight:bold">{{outlookTitle}}</label>
                </div>
                <div class="small-12">
                    <hr class="small-12"/>
                </div>
            </div>

            <div class="tool-slice row collapse">
                <div class="small-4">
                    <label class="tool-label">Outlook Days:</label>
                </div>
                <div class="small-8">
                    <select name="weatheroutlookOutlookDays" v-model="outlookDays" @change="systemsetting.saveState(10000)" v-bind:disabled="isDayReadonly">
                        <option value="1">Today</option>      
                        <option value="2">2 Days</option>      
                        <option value="3">3 Days</option>      
                        <option value="4">4 Days</option>      
                        <option value="6">6 Days</option>      
                        <option value="7">7 Days</option>      
                    </select>
                </div>
            </div>

            <div class="tool-slice row collapse">
                <div class="small-4">
                    <label class="tool-label">Outlook Times:</label>
                </div>
                <div class="small-8">
                    <select name="weatheroutlookReportType" v-model="reportType" @change="systemsetting.saveState(10000)" v-bind:disabled="isTimeReadonly">
                        <option value="1">Hourly</option>      
                        <option value="2">2 Hourly</option>      
                        <option value="3">3 Hourly</option>      
                        <option value="4">4 Hourly</option>      
                        <option value="6">6 Hourly</option>      
                        <option value="0">Others</option>      
                    </select>
                    <div v-show="reportType == 0">
                      <input type="text" v-model="editingReportHours" placeholder="hours(0-23) separated by ','" @blur="formatReportHours" @keyup="formatReportHours" v-bind:disabled="isTimeReadonly">
                    </div>
                </div>
                <div class="small-12"  v-show="outlookTool.toolid != 'weather-outlook-amicus'">
                    <hr class="small-12"/>
                </div>
            </div>
          </div>

          <div class="tool-slice row collapse" id="weatheroutlook-data-config" v-show="outlookTool.toolid != 'weather-outlook-amicus'">
            <div class="columns">
                <ul class="accordion" data-accordion>
                    <li class="accordion-item" data-accordion-item>
                        <!-- Accordion tab title -->
                        <a href="#" class="accordion-title">Daily Title</a>
                        <!-- Accordion tab content: it would start in the open state due to using the `is-active` state class. -->
                        <div class="accordion-content scroller" data-tab-content id="weatheroutlook-header">
                            <textarea type="text" rows="4" style="width:100%;resize:vertical" id="daily-title" v-model="dailyTitle" placeholder="{date}" @blur="checkDailyTitle" @keyup="checkDailyTitle" v-bind:readonly="isDailyTitleReadonly"> </textarea>
                            <div class="row feature-row status-row">
                                <div class="small-4">
                                    <div class="outlook-datasources">date</div>
                                </div>
                                <div class="small-8">
                                    <div class="outlook-datasources">outlook date</div>
                                </div>
                            </div>
                            <div v-for="ds in dailyDatasources" track-by="id" class="row feature-row status-row" >
                                <div class="small-4">
                                    <div class="outlook-datasources">{{ ds.var}} </div>
                                </div>
                                <div class="small-8">
                                    <div class="outlook-datasources">{{ ds.name}}</div>
                                </div>
                            </div>
                        </div>
                    </li>
                    <li class="accordion-item is-active" data-accordion-item>
                        <!-- Accordion tab title -->
                        <a href="#" class="accordion-title">Chosen Columns</a>
                        <!-- Accordion tab content: it would start in the open state due to using the `is-active` state class. -->
                        <div class="accordion-content" data-tab-content>
                            <div class="scroller" id="weatheroutlook-columns" style="margin-left:-16px;margin-right:-16px">
                            <div style="margin-left:16px;margin-right:16px">
                                <template v-for="(index,column) in (columnRevision && outlookColumns)" track-by="$index" >
                                    <template v-if="column.group">
                                    <div class='row feature-row {{column===selectedColumn?"feature-selected":""}}' @click="selectColumn(index,-1,column)" id="active-column-{{index}}">
                                        <div class="small-12">
                                            {{ column.group}}
                                            <div class="text-right float-right" v-show="!isColumnsReadonly">
                                                <a @click.stop.prevent="removeColumn(index,-1,column)" v-show="!column.required" class="button tiny secondary alert" title="Remove"><i class="fa fa-close"></i></a>
                                                <a v-bind:disabled="index <= 0" @click.stop.prevent="moveUp(index,-1,column)" title="Move Up" class="button tiny secondary">
                                                    <i class="fa fa-arrow-up"></i>
                                                </a>
                                                <a v-bind:disabled="index >= outlookColumns.length - 1" @click.stop.prevent="moveDown(index,-1,column)" title="Move Down" class="button tiny secondary">
                                                    <i class="fa fa-arrow-down"></i>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    <div v-for="(subindex,subcolumn) in columnRevision && column.datasources" track-by="id" class='row feature-row {{subcolumn===selectedColumn?"feature-selected":""}}'
                                        @click.stop.prevent="selectColumn(index,subindex,subcolumn)" id=active-column-{{index}}-{{subindex}} style="margin-left:0px;">
                                        <div class="small-12">
                                            {{ subcolumn.name}}
                                            <div class="text-right float-right" v-show="!isColumnsReadonly">
                                                <a @click.stop.prevent="removeColumn(index,subindex,subcolumn)" v-show="!subcolumn.required" class="button tiny secondary alert" title="Remove"><i class="fa fa-close"></i></a>
                                                <a v-bind:disabled="subindex <= 0" @click.stop.prevent="moveUp(index,subindex,subcolumn)" title="Move Up" class="button tiny secondary">
                                                    <i class="fa fa-arrow-up"></i>
                                                </a>
                                                <a v-bind:disabled="subindex >= column.datasources.length - 1" 
                                                    @click.stop.prevent="moveDown(index,subindex,subcolumn)" title="Move Down" class="button tiny secondary">
                                                    <i class="fa fa-arrow-down"></i>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    </template>
                                    <template v-if="column.id">
                                    <div class='row feature-row {{column===selectedColumn?"feature-selected":""}}' @click="selectColumn(index,-1,column)" id="active-column-{{index}}">
                                        <div class="small-12">
                                            {{ column.name}}
                                            <div class="text-right float-right" v-show="!isColumnsReadonly">
                                                <a @click.stop.prevent="removeColumn(index,-1,column)" class="button tiny secondary alert" v-show="!column.required" title="Remove"><i class="fa fa-close"></i></a>
                                                <a v-bind:disabled="index <= 0" @click.stop.prevent="moveUp(index,-1,column)" title="Move Up" class="button tiny secondary">
                                                    <i class="fa fa-arrow-up"></i>
                                                </a>
                                                <a v-bind:disabled="index >= outlookColumns.length - 1" @click.stop.prevent="moveDown(index,-1,column)" title="Move Down" class="button tiny secondary">
                                                    <i class="fa fa-arrow-down"></i>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    </template>
                                </template>
                            </div>
                            </div>

                            <div class="row" id="weatheroutlook-column-editor" style="margin-left:-10px;margin-right:-10px" >
                                <div class="small-4">
                                    <label class="tool-label">Title:</label>
                                </div>
                                <div class="small-8">
                                    <input type="text" v-model="editingColumnTitle" @blur="changeColumnTitle()" @keyup="changeColumnTitle" v-bind:disabled="isColumnsReadonly || !selectedColumn || selectedColumn.group">
                                </div>
                                <div class="small-4">
                                    <label class="tool-label">Group:</label>
                                </div>
                                <div class="small-8">
                                    <input type="text" v-model="editingColumnGroup" list="column-groups"  @blur="changeColumnGroup()" @keyup="changeColumnGroup"  v-bind:disabled="isColumnsReadonly || !selectedColumn">
                                    <datalist id="column-groups">
                                        <option v-for="group in columnGroups" track-by="$index" value="{{group}}">
                                    </datalist>
                                </div>
                            </div>
                        </div>
                    </li>
                    <li class="accordion-item" data-accordion-item>
                        <!-- Accordion tab title -->
                        <a href="#" class="accordion-title">Available Columns</a>
                        <!-- Accordion tab content: it would start in the open state due to using the `is-active` state class. -->
                        <div class="accordion-content scroller" data-tab-content id="weatheroutlook-datasources">

                            <div class="row">
                              <div class="switch tiny">
                                <input class="switch-input" id="toggleDailyDatasources" type="checkbox" v-bind:checked="showDailyDatasources" @change="showDailyDatasources=!showDailyDatasources" />
                                <label class="switch-paddle" for="toggleDailyDatasources">
                                  <span class="show-for-sr">Show daily datasources</span>
                                </label>
                              </div>
                              <label for="toggleDailyDatasources" class="side-label" >Show daily datasources</label>
                              <a @click.stop.prevent="refreshDatasources(true)"  title="Refresh" style="margin-left:120px" ><i class="fa fa-refresh"></i></a>
                            </div>

                            <template v-for="ds in datasources" track-by="id">
                              <div v-if="isShow(ds)" class="row feature-row status-row" >
                                <div class="small-12">
                                    {{ ds.name}}
                                    <div class="text-right float-right" >
                                       <div class="switch tiny" @click.stop >
                                           <input class="switch-input ctlgsw" id="outlook_ds_{{ $index }}" v-bind:disabled="isColumnsReadonly || ds.required"  type="checkbox" @change="toggleDatasource(ds)" v-bind:checked="isDatasourceSelected(ds)"/>
                                           <label class="switch-paddle" for="outlook_ds_{{ $index }}">
                                               <span class="show-for-sr">Toggle</span>
                                           </label>
                                        </div>
                                    </div>
                                </div>
                                <div class="small-6 datasource-desc">
                                    <div class="outlook-datasources">Type: {{ ds.metadata.type }}</div>
                                </div>
                                <div class="small-6 datasource-desc">
                                    <div class="outlook-datasources" v-if="isDegreeUnit(ds)">Unit: &deg;
                                    </div>
                                    <div class="outlook-datasources" v-if="ds.metadata.unit && !isDegreeUnit(ds)">Unit: {{ ds.metadata.unit}}
                                    </div>
                                </div>
                                <div class="small-12 datasource-desc">
                                    <div class="outlook-datasources">Title: {{ ds.options.title }}</div>
                                </div>
                                <div class="small-12 datasource-desc">
                                    <div class="outlook-datasources">Updated: {{ ds.metadata.refresh_time?ds.metadata.refresh_time.toLocaleString():"" }}</div>
                                </div>
                              </div>
                            </template>
                        </div>
                    </li>
                </ul>
            </div>
          </div>

        </div>
      </div>
    </div>

    <form id="get_weatheroutlook" name="weatheroutlook" action="{{env.gokartService + '/weatheroutlook/html'}}" method="post" target="weatheroutlook">
        <input type="hidden" name="data" id="weatheroutlook_data">
    </form>
  </div>
</template>

<style>
#weatheroutlook_control button{
    width: 48px;
    height: 48px;
    margin: 0;
}

.datasource-desc {
    font-style:italic;
    padding-left:24px;
    color:#6dd8ef;
    font-size:14px;
}

#weatheroutlook-data-config .accordion {
    background-color: transparent
}
#weatheroutlook-data-config .accordion-content {
    background-color: transparent
}
#daily-title.alert{
    background-color: rgba(171, 116, 107, 0.7);
}
.outlook-datasources {
    font-size: 100%;
}
#weatheroutlook_control .selected{
    background-color: #2199E8;
}
#weatheroutlook_control {
    position: absolute;
    left: auto;
    right: 16px;
    bottom: auto;
    padding: 0;
}

</style>

<script>
  import { ol,saveAs,$,moment,utils} from 'src/vendor.js'
  export default {
    store: {
        outlookSettings:'settings.weatheroutlook',
        screenHeight:'layout.screenHeight',
        leftPanelHeadHeight:'layout.leftPanelHeadHeight',
        activeMenu:'activeMenu',
        activeSubmenu:'activeSubmenu',
    },
    data: function () {
      return {
        format:"html",
        initialized:false,
        showDailyDatasources:false,
        editingReportHours:"",
        editingColumnTitle:"",
        editingColumnGroup:"",
        selectedRow:null,
        selectedDatasource:{},
        selectedIndex:-1,
        selectedSubindex:-1,
        selectedColumn:null,
        outlookTool:{},
        outlookTools:[
            {toolid:"weather-outlook-default",title:"Default 4 Day Weather Outlook",icon:"/dist/static/images/weather-outlook-default.svg",fixed_columns:true},
            {toolid:"weather-outlook-customized",title:"Customized Weather Outlook",icon:"/dist/static/images/weather-outlook-customized.svg",fixed_columns:false},
            {toolid:"weather-outlook-amicus",title:"Weather Outlook Amicus Export",icon:"/dist/static/images/weather-outlook-amicus.svg",fixed_columns:true}
        ],
        showSettings:false,
        revision:1,
        columnRevision:1,
      }

    },
    // parts of the template to be computed live
    computed: {
      loading: function () { return this.$root.loading },
      setting: function () { return this.$root.setting },
      map: function () { return this.$root.map },
      env: function () { return this.$root.env },
      systemsetting: function () { return this.$root.systemsetting },
      measure: function () { return this.$root.measure },
      active: function () { return this.$root.active },
      catalogue: function () { return this.$root.catalogue },
      annotations: function () { return this.$root.$refs.app.$refs.annotations },
      dailyDatasources:function() {
        return this.columnRevision && (this._datasources?this._datasources["dailyDatasources"]:[])
      },
      datasources:function() {
        return this.columnRevision && (this._datasources?this._datasources["datasources"]:[])
      },
      isDayReadonly:function() {
        return this.outlookTool.toolid === "weather-outlook-default"
      },
      isDailyTitleReadonly:function() {
        return this.outlookTool.toolid !== "weather-outlook-customized"
      },
      isTimeReadonly:function() {
        return this.outlookTool.toolid === "weather-outlook-default"
      },
      isColumnsReadonly:function() {
        return !this.initialized || this.outlookTool.toolid !== "weather-outlook-customized"
      },
      outlookTitle:function() {
        return this.outlookTool.title
      },
      outlookSetting:function() {
        return this.columnRevision && this.getOutlookSetting()
      },
      reportType:{
        get: function() {
            return this.revision && this.getReportType()
        },
        set: function(value) {
            this.setReportType(value)
            this.revision += 1
        }
      },
      reportHours:{
        get: function() {
            return this.revision && this.getReportHours()
        },
        set: function(value) {
            this.setReportHours(value)
            this.revision += 1
        }
      },
      dailyTitle:{
        get: function() {
            return this.revision && this.getDailyTitle()
        },
        set: function(value) {
            this.setDailyTitle(value)
            this.revision += 1
        }
      },
      outlookDays:{
        get: function() {
            return this.revision && this.getOutlookDays()
        },
        set: function(value) {
            this.setOutlookDays(value)
            this.revision += 1
        }
      },
      outlookColumns:{
        get: function() {
            return this.columnRevision && (this.initialized?this.getOutlookColumns():[])
        },
        set: function(value) {
            this.setOutlookColumns(value)
        }
      },
      columnGroups:{
        get: function() {
            return this.columnRevision && this.getColumnGroups()
        },
        set: function(value) {
            this.setColumnGroups(value)
        }
      },
      reportTimes:{
        get:function() {
            return this.revision && this.getReportTimes()
        },
        set:function(value) {
            this.setReportTimes(value)
        }
      },
      isControlSelected:function() {
        if (this.annotations) {
            return this.annotations.tool === this._weatheroutlookTool
        } else {
            return false
        }
      },
      selectedColumnTitle:{
        get:function(){
            if (this.selectedColumn === null || this.selectedColumn.group) {
                return ""
            }
            return (this.selectedColumn.options && this.selectedColumn.options.title) || this.selectedDatasource.options.title
        },
        set:function(value){
            if (this.selectedColumn === null || this.selectedColumn.group) {
                return 
            }
            value = value.trim()
            if (!value || this.selectedDatasource.options.title === value) {
                if (this.selectedColumn.options && "title" in this.selectedColumn.options) {
                    delete this.selectedColumn.options["title"]
                }
            } else {
                this.selectedColumn.options = this.selectedColumn.options || {}
                this.selectedColumn.options["title"] = value
            }
        }
      },
      tools:function() {
        return this.outlookTools
      },
    },
    watch:{
      isControlSelected:function(newValue,oldValue) {
        if (newValue) {
            this._overlay.setMap(this.map.olmap)
        } else {
            this._overlay.setMap(null)
        }
      },
      outlookDays:function(newValue,oldValue) {
        this.changeOutlookToolTitle()
      },
      outlookTool:function(newValue,oldValue) {
        this.adjustHeight()
      },
      outlookSetting:function(newValue,oldValue) {
        this.editingReportHours = newValue?newValue.reportHours:""
      },
      reportType:function(newValue,oldValue) {
        if (newValue === 0 || oldValue === 0) {
            this.adjustHeight()
        }
      }
    },
    // methods callable from inside the template
    methods: {
      adjustHeight:function() {
        if (this.activeMenu === "settings" && this.activeSubmenu === "weatheroutlook") {
            //the 'chosen columns' is selected by default, so the first time when the user entries into the sportoutlook setting panel, the 'column editor' should have valid height value.
            this._columnEditorHeight = this._columnEditorHeight || $("#weatheroutlook-column-editor").height()
            var height = this.screenHeight - this.leftPanelHeadHeight - $("#weatheroutlook-settings").height() - 200
            $("#weatheroutlook-header").height(height)
            $("#weatheroutlook-columns").height(height - this._columnEditorHeight)
            $("#weatheroutlook-datasources").height(height)
        }
      },
      open:function(options) {
        //active this module
        if (this.activeMenu !== "settings") {
            $("#menu-tab-settings-label").trigger("click")
        }
        if (this.activeSubmenu !== "weatheroutlook") {
            $("#weatheroutlook-label").trigger("click")
        }
        if(!$('#offCanvasLeft').hasClass('reveal-responsive')){
            $('#offCanvasLeft').toggleClass('reveal-responsive')
            this.map.olmap.updateSize()
        }

      },
      getOutlookTool:function(toolid) {
        return toolid?this.outlookTools.find(function(o) {return o.toolid === toolid}):this.outlookTool
      },
      getOutlookSetting:function(toolid){
        toolid = toolid || this.outlookTool.toolid
        if (toolid === "weather-outlook-default") {
            if (!this._defaultOutlookSetting) {
                this._defaultOutlookSetting = {
                }
            }
            return this.revision && this._defaultOutlookSetting
        } else {
            if (!this.outlookSettings[toolid]) {
                this.outlookSettings[toolid] = {
                }
            }
            return this.revision && this.outlookSettings[toolid]
        }
      },
      getReportType:function(toolid){
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        if (outlookSetting.reportType === null || outlookSetting.reportType === undefined) {
            if (toolid === "weather-outlook-default") {
                this.setReportType(0,toolid) //others
                this.setReportHours("9,12,15,18",toolid)
            } else if (toolid === "weather-outlook-customized") {
                this.setReportType(3,toolid) //3 hourly
            } else {
                this.setReportType(1,toolid) //hourly
            }
        }
        return outlookSetting.reportType
      },
      setReportType:function(value,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        outlookSetting.reportType = parseInt(value)
        outlookSetting.reportTimes = null
      },
      getReportHours:function(toolid) {
        if (this.getReportType(toolid) === 0) {
            return this.getOutlookSetting(toolid).reportHours
        } else {
            return ""
        }
      },
      setReportHours:function(value,toolid){
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        outlookSetting.reportHours = value
        if (this.getReportType(toolid) === 0) {
            outlookSetting.reportTimes = null
        }
      },
      getDailyTitle:function(toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        if (!outlookSetting.dailyTitle) {
            if (toolid === "weather-outlook-default") {
                this.setDailyTitle("{date} {weather}",toolid)
            } else if (toolid === "weather-outlook-customized") {
                this.setDailyTitle("{date} {weather}",toolid)
            } else {
                this.setDailyTitle("{date}",toolid)
            }
        }
        return outlookSetting.dailyTitle
      },
      setDailyTitle:function(value,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        outlookSetting.dailyTitle = value
      },
      getOutlookDays:function(toolid){
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        if (!(outlookSetting.outlookDays)) {
            if (toolid === "weather-outlook-default") {
                this.setOutlookDays(4,toolid) // 4 days
            } else if (toolid === "weather-outlook-customized") {
                this.setOutlookDays(4,toolid) // 4 days
            } else {
                this.setOutlookDays(2,toolid) // 2 days
            }
        }
        return outlookSetting.outlookDays
      },
      setOutlookDays:function(value,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        outlookSetting.outlookDays = parseInt(value)
      },
      getOutlookColumns:function(toolid){
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        if (!outlookSetting.outlookColumns || outlookSetting.outlookColumns.length === 0) {
            this.setOutlookColumns(null,toolid)
        }
        return outlookSetting.outlookColumns
      },
      setOutlookColumns:function(columns,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.tooid

        if (!columns || columns.length === 0) {
            if (toolid === "weather-outlook-default") {
                columns = [
                  {
                      workspace:"bom",
                      id:"IDW71034_WA_WxIcon_SFC_ICON",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71000_WA_T_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71001_WA_Td_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71018_WA_RH_SFC",
                  },
                  {
                      group:"10m Wind",
                      datasources:[
                          {
                              workspace:"bom",
                              id:"IDW71089_WA_Wind_Dir_SFC",
                          },
                          {
                              workspace:"bom",
                              id:"IDW71071_WA_WindMagKmh_SFC",
                          },
                          {
                              workspace:"bom",
                              id:"IDW71072_WA_WindGustKmh_SFC",
                          }
                      ]
                  },
                  {
                      workspace:"bom",
                      id:"IDW71127_WA_DF_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71139_WA_Curing_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71117_WA_FFDI_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71122_WA_GFDI_SFC",
                  },
                ]
            } else if (toolid === "weather-outlook-customized") {
                columns = [
                  {
                      workspace:"bom",
                      id:"IDW71034_WA_WxIcon_SFC_ICON",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71000_WA_T_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71001_WA_Td_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71018_WA_RH_SFC",
                  },
                  {
                      group:"10m Wind",
                      datasources:[
                          {
                              workspace:"bom",
                              id:"IDW71089_WA_Wind_Dir_SFC",
                          },
                          {
                              workspace:"bom",
                              id:"IDW71071_WA_WindMagKmh_SFC",
                          },
                          {
                              workspace:"bom",
                              id:"IDW71072_WA_WindGustKmh_SFC",
                          }
                      ]
                  },
                  {
                      workspace:"bom",
                      id:"IDW71127_WA_DF_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71139_WA_Curing_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71117_WA_FFDI_SFC",
                  },
                  {
                      workspace:"bom",
                      id:"IDW71122_WA_GFDI_SFC",
                  },
                ]
            } else {
                columns = [
                    {
                        workspace:"bom",
                        id:"IDW71000_WA_T_SFC",
                        options:{
                          title:"air_temperature"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71001_WA_Td_SFC",
                        options:{
                          title:"dewpoint_temperature"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71018_WA_RH_SFC",
                        options:{
                          title:"relative_humidity"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71089_WA_Wind_Dir_SFC",
                        options:{
                          title:"wind_direction"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71071_WA_WindMagKmh_SFC",
                        options:{
                          title:"wind_speed"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71072_WA_WindGustKmh_SFC",
                        options:{
                          title:"wind_gust_speed"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71111_WA_Wind_Dir_1500mAMSL",
                        options:{
                          title:"wind_direction_850hpa"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71110_WA_WindMagKmh_1500mAMSL",
                        options:{
                          title:"wind_speed_850hpa"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71117_WA_FFDI_SFC",
                        options:{
                          title:"forest_fire_danger_index"
                        }
                    },
                    {
                        workspace:"bom",
                        id:"IDW71122_WA_GFDI_SFC",
                        options:{
                          title:"grassland_fire_danger_index"
                        }
                    },
                ]
            }
        }

        var outlookTool = this.getOutlookTool(toolid)
        var vm = this
        outlookSetting.outlookColumns = columns
        var columnGroups = this.getColumnGroups(toolid)
        if (columnGroups.length > 0) {
            colmnGroups.length = 0
        }
        $.each(vm._datasources["datasources"],function(index,ds){
            if (!("selected" in ds)) {
                ds["selected"] = {}
            }
            ds["selected"][toolid] = false
        })

        var required = false
        for(var index = outlookSetting.outlookColumns.length - 1;index >= 0;index--) {
            column = outlookSetting.outlookColumns[index]
            if (column.group){
                required = false
                for(var subindex = column.datasources.length - 1;subindex >= 0;subindex--) {
                    subcolumn = column.datasources[subindex]
                    var ds = vm._datasources["datasources"].find(function(o){return o["workspace"] === subcolumn["workspace"] && o["id"] === subcolumn["id"]})
                    if (ds) {
                        ds["selected"][toolid] = true
                        subcolumn["name"] = ds["name"]
                        subcolumn["required"] = ds["required"]?true:false
                        required = required || subcolumn["required"]
                    } else {
                        //column is unavailable
                        column.datasources.splice(subindex,1)
                    }
                }
                column["required"] = required
                var groupIndex = columnGroups.findIndex(function(o){return o === column["group"]})
                if (column.datasources.length === 0) {
                    vm.outlookColumns.splice(index,1)
                    if (groupIndex >= 0) {
                        columnGroups.splice(groupIndex,1)
                    }
                } else if(groupIndex < 0) {
                    columnGroups.push(column["group"])
                    
                }
            } else {
                var ds = vm._datasources["datasources"].find(function(o){return o["workspace"] === column["workspace"] && o["id"] === column["id"]})
                if (ds) {
                    ds["selected"][toolid] = true
                    column["name"] = ds["name"]
                    column["required"] = ds["required"]?true:false
                } else {
                    //column is unavailable
                    outlookSetting.outlookColumns.splice(index,1)
                }

            }
        }
        //add required columns if the outlook tools's columns is not  fixed 
        if (!outlookTool.fixed_columns) {
            $.each(vm._datasources["datasources"],function(index,ds){
                if (ds["required"] && !ds["selected"][toolid]) {
                    vm.toggleDatasource(ds,true,null,null,toolid) 
                }
            })
        }

        columnGroups.sort()
        if (toolid === this.outlookTool.toolid) {
            this.editingColumnTitle = ""
            this.editingColumnGroup = ""
            this.selectedRow = null
            this.selectedDatasource = null
            this.selectedIndex = -1
            this.selectedSubindex = -1
            this.selectedColumn = null
            this.columnRevision += 1
        }

      },
      getColumnGroups:function(toolid){
        toolid = toolid || this.outlookTool.toolid
        if (!(toolid in this._columnGroups)) {
            this._columnGroups[toolid] = []
        }
        return this._columnGroups[toolid]
      },
      setColumnGroups:function(value,toolid) {
        toolid = toolid || this.outlookTool.toolid
        this._columnGroups[toolid] = value
      },
      getReportTimes:function(toolid) {
        toolid = toolid || this.outlookTool.toolid
        var outlookSetting = this.getOutlookSetting(toolid)
        if (!outlookSetting.reportTimes) {
            var reportTimes = []
            var reportType = this.getReportType(toolid)
            if (reportType > 0) {
                var hour = 0;
                while (hour < 24) {
                    if (hour % reportType === 0) {
                        if (hour < 10) {
                            reportTimes.push("0" + hour + ":00:00")
                        } else {
                            reportTimes.push(hour + ":00:00")
                        }
                    }
                    hour += 1
                }
            } else {
                var reportHours = this.getReportHours(toolid)
                if (reportHours != null){
                    var hours = this.reportHours + "";
                    if (hours.length > 0) {
                        $.each(hours.split(","),function(index,hour){
                            if (hour < 10) {
                                reportTimes.push("0" + hour + ":00:00")
                            } else {
                                reportTimes.push(hour + ":00:00")
                            }
                        })
                    }
                }
            }
            this.setReportTimes(reportTimes,toolid)
        }
        return outlookSetting.reportTimes
      },
      setReportTimes:function(value,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        outlookSetting.reportTimes = value
      },
      changeOutlookToolTitle:function(toolid) {
        var outlookTool = this.getOutlookTool(toolid)
        if (outlookTool.toolid === "weather-outlook-customized") {
            outlookTool.title = "Customised " + this.getOutlookDays(toolid) + " Day Weather Outlook"
        } else if (outlookTool.toolid === "weather-outlook-amicus") {
            outlookTool.title = this.getOutlookDays(toolid) + " Day Weather Outlook Amicus Export"
        }
      },
      selectSetting:function(s) {
        this.showSettings = false
        if (this.outlookTool === s) {
            return
        }
        this.outlookTool = s
      },
      selectTool:function(tool) {
        if (tool.toolid !== "weather-outlook-default") {
            this.open()
        }
        if (this.outlookTool === tool) {
            return
        }
        this.outlookTool = tool
        this.revsion += 1
        this.columnRevision += 1
      },
      toggleTool: function (enable) {
        if (!this._weatheroutlookTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else if (enable === true && this.annotations.tool === this._weatheroutlookTool) {
            //already enabled
            return
        } else if (enable === false && this.annotations.tool !== this._weatheroutlookTool) {
            //already disabled
            return
        } else if (this.annotations.tool === this._weatheroutlookTool) {
            this.annotations.setTool(this.annotations.currentTool,true)
        } else  {
            this.annotations.setTool(this._weatheroutlookTool)
        }
      },
      isToolActivated:function(tool) {
        return this.isControlSelected
      },
      isDegreeUnit:function(ds) {
        return ds.metadata.unit === "C"
      },
      selectColumn:function(index,subindex,column) {
        if (this.selectedRow) {
            this.selectedRow.removeClass("feature-selected")
        }
        this.selectedIndex = index
        this.selectedSubindex = (subindex < 0 || subindex === null || subindex == undefined)?-1:subindex
        this.selectedRow = this.selectedSubindex == -1?$("#active-column-" + this.selectedIndex):$("#active-column-" + this.selectedIndex + "-" + this.selectedSubindex)
        this.selectedColumn = column
        if (column.group) {
            //the selected column is a group
            this.selectedDatasource = null
            this.editingColumnTitle = ""
            this.editingColumnGroup = column.group
        } else {
            //the selected column is a column
            this.selectedDatasource = this._datasources["datasources"].find(function(o){return o.id === column.id})
            this.editingColumnTitle = this.selectedColumnTitle
            this.editingColumnGroup = subindex >= 0 ?this.outlookColumns[index]["group"]:""
        }

        this.selectedRow.addClass("feature-selected")
      },
      changeColumnTitle:function(event) {
        if (event && event.type === "keyup" && event.keyCode !== 13) {  
            return
        }
        if (this.selectedColumnTitle === this.editingColumnTitle) {
            //not changed
            return
        }
        this.selectedColumnTitle = this.editingColumnTitle
        this.systemsetting.saveState(10000)
      },
      changeColumnGroup:function(event) {
        if (event && event.type === "keyup" && event.keyCode !== 13) {  
            return
        }
        this.editingColumnGroup = this.editingColumnGroup.trim()
        var vm = this
        if (this.selectedColumn.group) {
            if (this.editingColumnGroup === this.selectedColumn.group) {
                return
            }
            //remove the old group
            var groupIndex = this.columnGroups.findIndex(function(o){return o === vm.selectedColumn["group"]})
            if (groupIndex >= 0) {
                this.columnGroups.splice(groupIndex,1)
            }

            if (this.editingColumnGroup) {
                //change group name
                groupIndex = this.outlookColumns.findIndex(function(o) {return o.group?o.group === vm.editingColumnGroup:false})
                if (groupIndex >= 0) {
                    //group already exist,move the columns to existing groups
                    this.outlookColumns[groupIndex].datasources.push.apply(this.outlookColumns[groupIndex].datasources,this.selectedColumn.datasources)
                    //remove the old group
                    this.outlookColumns.splice(this.selectedIndex,1)
                    if (this.selectedIndex < groupIndex) {
                        this.selectedIndex = groupIndex - 1
                    } else {
                        this.selectedIndex = groupIndex
                    }
                    this.selectedIndex = groupIndex
                    this.selectedSubindex = -1
                    this.selectedColumn = this.outlookColumns[groupIndex]
                    this.selectedRow = null
                    this.selectedDatasource = null
                    this.editingColumnTitle = ""

                } else {
                    //group does not exist, rename the group
                    this.outlookColumns[vm.selectedIndex]["group"] = this.editingColumnGroup
                    this.columnGroups.push(this.editingColumnGroup)
                    this.columnGroups.sort()
                }
                

            } else {
                //remove group
                this.outlookColumns.splice(this.selectedIndex,1)
                $.each(this.selectedColumn.datasources,function(index,col){
                    vm.outlookColumns.splice(vm.selectedIndex + index,0,col)
                })
                this.selectedIndex = -1
                this.selectedSubindex = -1
                this.selectedColumn = null
                this.selectedRow = null
                this.selectedDatasource = null
                this.editingColumnTitle = ""
                this.editingColumnGroup = ""
            }
        } else {
            if (this.editingColumnGroup) {
                if (this.selectedSubindex >=0  && this.outlookColumns[this.selectedIndex]["group"] === this.editingColumnGroup) {
                    //not changed
                    return
                }
            } else if (this.selectedSubindex < 0) {
                //not changed
                return
            }
            //group changed
            if (this.selectedSubindex >= 0) {
                //already in a group, remove it from old group
                this.outlookColumns[this.selectedIndex]["datasources"].splice(this.selectedSubindex,1)
                if (this.outlookColumns[this.selectedIndex]["datasources"].length === 0) {
                    //group is empty, remove it
                    var groupIndex = this.columnGroups.findIndex(function(o){return o === vm.outlookColumns[vm.selectedIndex]["group"]})
                    if (groupIndex >= 0) {
                        this.columnGroups.splice(groupIndex,1)
                    }
                    this.outlookColumns.splice(this.selectedIndex,1)
                } else {
                    this.selectedIndex += 1
                }
            } else {
                //not in a group, remove it from outlookColumns
                this.outlookColumns.splice(this.selectedIndex,1)
            }
            if (this.editingColumnGroup) {
                var groupIndex = this.outlookColumns.findIndex(function(o) {return o.group?o.group === vm.editingColumnGroup:false})
                if (groupIndex >= 0) {
                    //new  group already exist, add it into the existing group
                    this.outlookColumns[groupIndex]["datasources"].push(this.selectedColumn)
                    this.selectedIndex = groupIndex
                    this.selectedSubindex = this.outlookColumns[groupIndex]["datasources"].length - 1
                } else {
                    //group doesn't exist, add a new group
                    this.outlookColumns.splice(this.selectedIndex,0,{group:this.editingColumnGroup,datasources:[this.selectedColumn]})
                    this.selectedSubindex = 0
                    this.columnGroups.push(this.editingColumnGroup)
                    this.columnGroups.sort()
                }
            } else {
                //not in a group
                this.outlookColumns.splice(this.selectedIndex,0,this.selectedColumn)
                this.selectedSubindex = -1
                
            }
        }
        this.columnRevision += 1

      },
      //toggle datasource
      //ds: the datasource
      //add: add if true else remove
      //index, subindex: used to improve performance during removing
      //toolid: which tool's setting will be changed, if missing, the current tool's setting will be changed
      toggleDatasource:function(ds,add,index,subindex,toolid) {
        var outlookSetting = toolid?this.getOutlookSetting(toolid):this.outlookSetting
        toolid = toolid || this.outlookTool.toolid
        if (ds) {
            if (add === undefined || add === null) {
                ds["selected"][toolid] = !(ds["selected"][toolid] || false)
            } else {
                ds["selected"][toolid] = add
            }
        }
        var vm = this
        if (ds && ds["selected"][toolid]) {
            //add
            if (ds["options"] && ds["options"]["group"]) {
                //has default group
                group = ds["options"] && ds["options"]["group"]
                var groupIndex = outlookSetting.outlookColumns.findIndex(function(o) {return o.group?o.group === group:false})
                if (groupIndex >= 0) {
                    //group already exist
                    outlookSetting.outlookColumns[groupIndex]["required"] = outlookSetting.outlookColumns[groupIndex]["required"] || (ds["required"] || false)
                    outlookSetting.outlookColumns[groupIndex]["datasources"].push({workspace:ds["workspace"],id:ds["id"],name:ds["name"],required:ds["required"] || false})
                } else {
                    //group does not exist
                    outlookSetting.outlookColumns.push({
                        group:group,
                        datasources:[{workspace:ds["workspace"],id:ds["id"],name:ds["name"],required:ds["required"] || false}]
                    })
                }
                var columnGroups = this.getColumnGroups(toolid)
                groupIndex = columnGroups.findIndex(function(o) {return o === group})
                if (groupIndex < 0) {
                    columnGroups.push(group)
                    columnGroups.sort()
                }
            } else {
                //no default group
                outlookSetting.outlookColumns.push({workspace:ds["workspace"],id:ds["id"],name:ds["name"],required:ds["required"] || false})
            }

        } else {
            //remove
            if (ds["required"]) {
                //required column, can't remove
                return
            }
            if (index === null || index === undefined) {
                $.each(outlookSetting.outlookColumns,function(i,column){
                    if (column.group) {
                        j = column.datasources.findIndex(function(o){ return o["workspace"] === ds["workspace"] && o["id"] === ds["id"]})
                        if (j >= 0) {
                            index = i
                            subindex = j
                            return false
                        }
                    } else if (column["workspace"] === ds["workspace"] && column["id"] === ds["id"]){
                        index = i
                        subindex = -1
                        return false
                    }
                })
            }
            if (subindex >= 0) {
                outlookSetting.outlookColumns[index]["datasources"].splice(subindex,1)
                if (toolid === this.outlookTool.toolid) {
                    if (this.selectedIndex === index && this.selectedSubindex === subindex) {
                        this.selectedIndex = -1
                        this.selectedSubindex = -1
                        this.selectedColumn = null
                        this.selectedRow = null
                        this.selectedDatasource = null
                        this.editingColumnTitle = ""
                        this.editingColumnGroup = ""
                    } else if (this.selectedIndex === index && this.selectedSubindex > subindex) {
                        this.selectedSubindex -= 1
                    }
                }
                if (outlookSetting.outlookColumns[index]["datasources"].length === 0) {
                    var columnGroups = this.getColumnGroups(toolid)
                    var groupIndex = columnGroups.findIndex(function(o){return o === vm.outlookColumns[index]["group"]})
                    if (groupIndex >= 0) {
                        columnGroups.splice(groupIndex,1)
                    }
                    this.outlookColumns.splice(index,1)
                    if (toolid === this.outlookTool.toolid) {
                        if (this.selectedIndex > index) {
                            this.selectedIndex -= 1
                        }
                    }
                }
            } else if (index >= 0) {
                outlookSetting.outlookColumns.splice(index,1)
                if (toolid === this.outlookTool.toolid) {
                    if (this.selectedIndex === index) {
                        this.selectedIndex = -1
                        this.selectedSubindex = -1
                        this.selectedColumn = null
                        this.selectedRow = null
                        this.selectedDatasource = null
                        this.editingColumnTitle = ""
                        this.editingColumnGroup = ""
                    } else if(this.selectedIndex > index) {
                        this.selectedIndex -= 1
                    }
                }
            }
        }
        this.systemsetting.saveState(10000)
        if (toolid === this.outlookTool.toolid) {
            this.columnRevision += 1
        }
      },
      moveDown:function(index,subindex,column) {
        if (subindex >= 0) {
            if (index >= this.outlookColumns.length || index < 0) {
                return
            }
            if (subindex >= this.outlookColumns[index]["datasources"].length - 1 || subindex < 0) {
                return
            }
        } else {
            if (index >= this.outlookColumns.length - 1 || index < 0) {
                return
            }
        }
        if (subindex >= 0) {
            this.outlookColumns[index]["datasources"][subindex] = this.outlookColumns[index]["datasources"][subindex + 1]
            this.outlookColumns[index]["datasources"][subindex + 1] = column
            if (this.selectedSubindex === subindex ) {
                this.selectedSubindex += 1
            } else if (this.selectedSubindex === subindex - 1) {
                this.selectedSubindex -= 1
            }
        } else {
            this.outlookColumns[index] = this.outlookColumns[index + 1]
            this.outlookColumns[index + 1] = column
            if (this.selectedIndex === index ) {
                this.selectedIndex += 1
            } else if (this.selectedIndex === index - 1) {
                this.selectedIndex -= 1
            }
        }
     
        this.systemsetting.saveState(10000)
        this.columnRevision += 1
      },
      moveUp:function(index,subindex,column) {
        if (subindex >= 0) {
            if (index >= this.outlookColumns.length || index < 0) {
                return
            }
            if (subindex >= this.outlookColumns[index]["datasources"].length || subindex <= 0) {
                return
            }
        } else {
            if (index >= this.outlookColumns.length || index <= 0) {
                return
            }
        }
        if (subindex >= 0) {
            this.outlookColumns[index]["datasources"][subindex] = this.outlookColumns[index]["datasources"][subindex - 1]
            this.outlookColumns[index]["datasources"][subindex - 1] = column
            if (this.selectedSubindex === subindex ) {
                this.selectedSubindex -= 1
            } else if (this.selectedSubindex === subindex - 1) {
                this.selectedSubindex += 1
            }
        } else {
            this.outlookColumns[index] = this.outlookColumns[index - 1]
            this.outlookColumns[index - 1] = column
            if (this.selectedIndex === index ) {
                this.selectedIndex -= 1
            } else if (this.selectedIndex === index - 1) {
                this.selectedIndex += 1
            }
        }
        this.systemsetting.saveState(10000)
        this.columnRevision += 1
      },
      removeColumn:function(index,subindex,column) {
        var vm = this
        if (column.required) return
        if (column.group) {
            //remove group
            for(var subindex = column.datasources.length - 1;subindex >= 0;subindex--) {
                var datasource = vm._datasources["datasources"].find(function(o) {return column.datasources[subindex]["workspace"] === o["workspace"] && column.datasources[subindex]["id"] === o["id"]})
                vm.toggleDatasource(datasource,false,index,subindex)
            }
        } else {
            var datasource = this._datasources["datasources"].find(function(o) {return column["workspace"] === o["workspace"] && column["id"] === o["id"]})
            this.toggleDatasource(datasource,false,index,subindex)
        }
      },
      isDatasourceSelected:function(ds) {
        try {
            return this.columnRevision && ds["selected"][this.outlookTool.toolid]
        } catch (ex) {
            return false
        }

      },
      isShow:function(ds) {
        return ds["metadata"]["type"] != "Daily" || this.showDailyDatasources
      },
      formatReportHours(event) {
        if (event && event.type === "keyup" && event.keyCode !== 13) {  
            return
        }
        var hours = ""
        $.each(this.editingReportHours.split(','),function(index,hour) {
            hour = parseInt(hour.trim())
            if (!isNaN(hour) && hour >= 0 && hour < 24) {
                if (hours === "") {
                    hours = hour
                } else {
                    hours += "," + hour
                }
            }
        })
        this.editingReportHours = hours
        if (this.reportHours === hours) {
            return
        }
        this.reportHours = hours
        this.systemsetting.saveState(10000)
      },
      getDailyData:function(toolid) {
        toolid = toolid || this.outlookTool.toolid
        if (!this._dailyData[toolid]) {
            var result;
            var dailyVars = {}
            var ds = null
            var varPattern = null
            var outlookSetting = (toolid)?this.getOutlookSetting(toolid):this.outlookSetting
            var title = outlookSetting.dailyTitle
            var rerun = true
            var unavailableVars = null
            while (rerun) {
                varPattern = /\{([^\}]+)\}/g
                rerun = false
                while(result = varPattern.exec(title || "")) {
                    if (result[1] === "date") {
                    } else if (!(ds = this._datasources["dailyDatasources"].find(function(ds){return ds["var"] === result[1]}))) {
                        if (unavailableVars === null) {
                            unavailableVars = result[1]
                        } else {
                            unavailableVars += " , " + result[1]
                        }
                        title = title.replace(result[0],"N/A")
                        rerun = true
                        break
                    } else {
                        dailyVars[result[1]] = {workspace:ds["workspace"],id:ds["id"]}
                    }
                }
            }
            this._dailyData[toolid] = [title,dailyVars,unavailableVars]
        }
        return this._dailyData[toolid]
      },
      checkDailyTitle(event) {
        if (event.type === "keyup" && event.keyCode !== 13) {
            this._dailyData[this.outlookTool.toolid] = null
            return
        }
        $("#daily-title").removeClass('alert')
        var dailyData = this.getDailyData(true)
        if (dailyData[2] !== null) {
            $("#daily-title").addClass('alert')
            alert("The variables (" + unavailableVars + ") are unavailable");
        } else {
            this.systemsetting.saveState(10000)
        }
      },
      loadDatasources:function() {
        var vm = this
        this._weatheroutlookStatus.phaseBegin("load_datasources",80,"Load datasources")
        this.refreshDatasources(true,function(){
            vm._weatheroutlookStatus.phaseEnd("load_datasources")
            vm.initialized = true
            vm.columnRevision += 1
        },function(msg){
            vm._weatheroutlookStatus.phaseFailed("load_datasources","Failed to loading datasources. status = " + msg)
        })
      },
      refreshDatasources:function(refresh,callback,failedCallback) {
        var vm = this
        this._datasources = []
        $.ajax({
            url: vm.env.gokartService + "/outlookmetadata" + (refresh?"?refresh=true":""),
            method:"GET",
            dataType:"json",
            success: function (response, stat, xhr) {
                $.each(response["datasources"],function(index,datasource){
                    if (datasource["metadata"] && datasource["metadata"]["refresh_time"]) {
                        datasource["metadata"]["refresh_time"] = moment.tz(datasource["metadata"]["refresh_time"],"YYYY-MM-DD HH:mm:ss","Australia/Perth")
                    }
                })
                vm._datasources = {"datasources":response["datasources"],"dailyDatasources":[]}
                $.each(vm._datasources["datasources"],function(index,ds){
                    if (ds["var"] && ds["metadata"]["type"] === "Daily") {
                        vm._datasources["dailyDatasources"].push(ds)
                    }
                })
                vm.columnRevision += 1
                vm.$nextTick(function(){
                    vm._dailyData = {}
                    vm._columnGroups = {}
                    var outlookSetting = null
                    var outlookTool = null
                    $.each(vm.outlookTools,function(index,tool){
                        outlookSetting = vm.getOutlookSetting(tool.toolid)
                        outlookTool = vm.getOutlookTool(tool.toolid)
                        if (outlookTool.fixed_columns) {
                            vm.setOutlookColumns(null,tool.toolid)
                        } else {
                            outlookSetting = vm.getOutlookSetting(tool.toolid)
                            vm.setOutlookColumns(outlookSetting.outlookColumns,tool.toolid)
                        }
                    })
                })
                if (callback) {callback()}
            },
            error: function (xhr,status,message) {
                var msg = xhr.status + " : " + (xhr.responseText || message)
                alert(msg)
                if (failedCallback) {failedCallback(msg)}
            },
            xhrFields: {
              withCredentials: true
            }
        })
      },
      setPosition:function(coordinate) {
        this._features.clear()
        this._features.push(new ol.Feature({geometry:new ol.geom.Point(coordinate)}))
      },
      getWeatherOutlook:function(coordinate) {
        if (this.reportTimes.length === 0) {
            alert("No weather outlook times are configured in settings module")
            return
        }
        var vm = this
        var _getWeatherOutlook = function(position) {
            var requestData = null;
            var format = vm.format
            var dailyData = vm.getDailyData()
            if (dailyData[2] !== null && dailyData[2] !== "" && !confirm("The variables (" + dailyData[2] + ") are unavailable.\r\nDo you want to continue?")) {
                return
            }
            if (vm.outlookTool.toolid === "weather-outlook-amicus") {
                requestData = {
                    point:coordinate,
                    options: {
                        title:vm.outlookDays + " Day Weather Outlook for " + position + "(" + Math.round(coordinate[0] * 10000) / 10000 + "," + Math.round(coordinate[1] * 10000) / 10000 + ")",
                        position:position,
                        latitude:Math.round(coordinate[1] * 10000) / 10000,
                        longitude:Math.round(coordinate[0] * 10000) / 10000,
                        no_data:""
                    },
                    outlooks:[
                        {
                            days:utils.getDatetimes(["00:00:00"],vm.outlookDays,1).map(function(dt) {return dt.format("YYYY-MM-DD")}),
                            times:vm.reportTimes,
                            min_time:moment().format("YYYY-MM-DD HH:00:00"),
                            options:{
                                expired:1 //unit:hour, the exipre time of each outlook in times
                            },
                            times_data:vm.outlookColumns,
                        }
                    ]
                }
                format = "amicus"
            } else {
                requestData = {
                    point:coordinate,
                    options: {
                        title:vm.outlookDays + " Day Weather Outlook for " + position + "(" + Math.round(coordinate[0] * 10000) / 10000 + "," + Math.round(coordinate[1] * 10000) / 10000 + ")",
                    },
                    outlooks:[
                        {
                            days:utils.getDatetimes(["00:00:00"],vm.outlookDays,1).map(function(dt) {return dt.format("YYYY-MM-DD")}),
                            times:vm.reportTimes,
                            options:{
                                daily_title_pattern: dailyData[0] || "{date}"
    
                            },
                            daily_data:dailyData[1] || {},
                            times_data:vm.outlookColumns,
                        }
                    ]
                }
            }
            if (format === "html") {
                $("#weatheroutlook_data").val(JSON.stringify(requestData))
                utils.submitForm("get_weatheroutlook",{width: (screen.width > 1890)?1890:screen.width, height:(screen.height > 1060)?1060:screen.height},true)
            } else {
                try{
                    var req = new window.XMLHttpRequest()
                    req.open('POST', vm.env.gokartService + "/weatheroutlook/" + format)
                    req.responseType = 'blob'
                    req.withCredentials = true
                    req.onload = function (event) {
                        try{
                            if (req.status >= 400) {
                                var reader = new FileReader()
                                reader.addEventListener("loadend",function(e){
                                    alert(e.target.result)
                                })
                                reader.readAsText(req.response)
                            } else {
                                var filename = null
                                if (req.getResponseHeader("Content-Disposition")) {
                                    var matches = vm._filename_re.exec(req.getResponseHeader("Content-Disposition"))
                                    filename = (matches && matches[1])? matches[1]: null
                                }
                                if (!filename) {
                                    filename = "weather_outlook_" + moment().format("YYYYMMDD_HHmm") + "." + format ;
                                }
                                saveAs(req.response, filename)
                            }
                        } catch(ex) {
                            alert(ex.message || ex)
                        }
                    }
                    var formData = new window.FormData()
                    formData.append('data', JSON.stringify(requestData))
                    req.send(formData)
                }catch(ex) {
                    callback(false,ex.message || ex)
                }
            }
        }

        this.map.getPosition(coordinate,_getWeatherOutlook)
        
      },
    },
    created:function() {
      this._dailyData = {}
      this._columnGroups = {}
      this.outlookTool = this.outlookTools[0]
    },
    ready: function () {
      var vm = this
      this._filename_re = new RegExp("filename=[\'\"](.+)[\'\"]")
      this._weatheroutlookStatus = vm.loading.register("weatheroutlook","BOM Spot Outlook Component")

      this._weatheroutlookStatus.phaseBegin("initialize",20,"Initialize")

      this.editingReportHours = this.reportHours

      this.loadDatasources()

      var map = this.$root.map

      this._features = new ol.Collection()
      this._features.on("add",function(event){
        vm.getWeatherOutlook(event.element.getGeometry().getCoordinates())
      })
      this._style =  new ol.style.Style({
          image: new ol.style.Icon({
            src: "dist/static/images/pin.svg",
            anchorOrigin:"bottom-left",
            anchorXUnits:"pixels",
            anchorYUnits:"pixels",
            anchor:[8,0]
          })
      })
      this._source = new ol.source.Vector({
          features:this._features
      })
      this._overlay = new ol.layer.Vector({
          source: this._source,
          style: this._style
      })

      //initialize the overlay and interactions
      var weatheroutlookInter = new ol.interaction.Draw({
          source: this._source,
          type: 'Point',
          style: this._style
      });

      weatheroutlookInter.on('drawend',function(){
        vm._features.clear()
      }, this)

      this._weatheroutlookTool = {
        name: 'WeatherOutlook',
        keepSelection:true,
        interactions:[
            weatheroutlookInter
        ]
      }

      this.annotations.tools.push(this._weatheroutlookTool)

      this.adjustHeight()

      var vm = this
      $.each(this.outlookTools,function(index,tool){
          vm.changeOutlookToolTitle(tool.toolid)
      })

      this._weatheroutlookStatus.phaseEnd("initialize")

    }
  }
</script>
